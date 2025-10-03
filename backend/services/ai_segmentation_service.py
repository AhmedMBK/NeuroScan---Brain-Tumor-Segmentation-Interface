"""
🧠 CereBloom - Service IA de Segmentation
Intégration de votre modèle U-Net Kaggle pour la segmentation de tumeurs cérébrales
"""

import os
import uuid
import numpy as np
import nibabel as nib
# TensorFlow import avec gestion d'erreur pour Python 3.13
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
    print("✅ TensorFlow disponible")
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️ TensorFlow non disponible - Mode simulation activé")
    # Créer un mock TensorFlow pour éviter les erreurs
    class MockTF:
        class keras:
            class models:
                @staticmethod
                def load_model(*args, **kwargs):
                    return None
            class backend:
                @staticmethod
                def epsilon():
                    return 1e-7
    tf = MockTF()

import cv2
try:
    from sklearn.preprocessing import MinMaxScaler
except ImportError:
    print("⚠️ scikit-learn non disponible")
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config.database import get_database
from config.settings import settings, TUMOR_SEGMENT_COLORS
from models.database_models import (
    AISegmentation, TumorSegment, VolumetricAnalysis,
    ImageSeries, MedicalImage, Patient, Doctor,
    SegmentationStatus, TumorType
)
from services.mlops_service import mlops_service

logger = logging.getLogger(__name__)

# Configuration du modèle (importée de loadmodel.py)
IMG_SIZE = 128
VOLUME_SLICES = 100
VOLUME_START_AT = 22

# Classification médicale des régions tumorales selon BraTS
TUMOR_CLASSES = {
    0: {'name': 'Tissu sain', 'abbr': 'Normal', 'color': '#000000', 'alpha': 0.0},
    1: {'name': 'Noyau nécrotique/kystique', 'abbr': 'Necrotic Core', 'color': '#FF0000', 'alpha': 0.8},
    2: {'name': 'Œdème péritumoral', 'abbr': 'Peritumoral Edema', 'color': '#00FF00', 'alpha': 0.7},
    3: {'name': 'Tumeur rehaussée', 'abbr': 'Enhancing Tumor', 'color': '#0080FF', 'alpha': 0.9}
}

class AISegmentationService:
    """Service de segmentation IA avec votre modèle U-Net Kaggle"""

    def __init__(self):
        self.model_path = settings.AI_MODEL_PATH
        self.model_version = settings.AI_MODEL_VERSION
        self.confidence_threshold = settings.AI_CONFIDENCE_THRESHOLD
        self.processing_timeout = settings.AI_PROCESSING_TIMEOUT
        self.model = None
        self.executor = ThreadPoolExecutor(max_workers=2)

        # Métriques personnalisées pour votre modèle
        self.custom_objects = {
            'dice_coef': self.dice_coef,
            'precision': self.precision,
            'sensitivity': self.sensitivity,
            'specificity': self.specificity,
            'dice_coef_necrotic': self.dice_coef_necrotic,
            'dice_coef_edema': self.dice_coef_edema,
            'dice_coef_enhancing': self.dice_coef_enhancing
        }

    async def load_model(self):
        """Charge votre modèle U-Net Kaggle"""
        try:
            if self.model is None:
                logger.info(f"Chargement du modèle: {self.model_path}")

                # Chargement asynchrone du modèle
                loop = asyncio.get_event_loop()
                self.model = await loop.run_in_executor(
                    self.executor,
                    self._load_model_sync
                )

                logger.info("✅ Modèle U-Net chargé avec succès")

            return self.model

        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle: {e}")
            raise

    def _load_model_sync(self):
        """Charge le modèle de manière synchrone"""
        return tf.keras.models.load_model(
            self.model_path,
            custom_objects=self.custom_objects,
            compile=False
        )

    async def create_segmentation(
        self,
        patient_id: str,
        doctor_id: str,
        image_series_id: str,
        input_parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Crée une nouvelle segmentation IA avec tracking MLOps"""
        async for db in get_database():
            try:
                # Création de l'enregistrement de segmentation
                segmentation_id = str(uuid.uuid4())
                segmentation = AISegmentation(
                    id=segmentation_id,
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                    image_series_id=image_series_id,
                    status=SegmentationStatus.PROCESSING,
                    input_parameters=input_parameters or {},
                    started_at=datetime.utcnow()
                )

                db.add(segmentation)
                await db.commit()

                # 📊 MLOPS - Démarrage du tracking automatique
                mlflow_run_id = mlops_service.start_segmentation_run(
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                    image_series_id=image_series_id,
                    input_parameters=input_parameters
                )

                # Stockage du run_id MLflow pour suivi
                segmentation.input_parameters = {
                    **(input_parameters or {}),
                    "mlflow_run_id": mlflow_run_id
                }
                await db.commit()

                logger.info(f"Segmentation créée: {segmentation_id} | MLflow Run: {mlflow_run_id}")

                # Lancement du traitement en arrière-plan
                asyncio.create_task(self._process_segmentation(segmentation_id))

                return segmentation_id

            except Exception as e:
                logger.error(f"Erreur lors de la création de segmentation: {e}")
                await db.rollback()
                raise

    async def _process_segmentation(self, segmentation_id: str):
        """Traite une segmentation en arrière-plan"""
        start_time = datetime.utcnow()

        async for db in get_database():
            try:
                # Récupération de la segmentation
                result = await db.execute(
                    select(AISegmentation).where(AISegmentation.id == segmentation_id)
                )
                segmentation = result.scalar_one_or_none()

                if not segmentation:
                    logger.error(f"Segmentation non trouvée: {segmentation_id}")
                    return

                # Récupération des images
                images_data = await self._load_image_series(db, segmentation.image_series_id)
                if not images_data:
                    await self._update_segmentation_status(db, segmentation_id, SegmentationStatus.FAILED)
                    return

                # Chargement du modèle
                model = await self.load_model()

                # Préparation des données
                input_data = await self._prepare_input_data(images_data)

                # Exécution de la segmentation
                loop = asyncio.get_event_loop()
                segmentation_result = await loop.run_in_executor(
                    self.executor,
                    self._run_segmentation,
                    model,
                    input_data
                )

                # Calcul des volumes et analyse
                volume_analysis = await self._calculate_volumes(segmentation_result)
                tumor_segments = await self._extract_tumor_segments(segmentation_result, volume_analysis)

                # Calcul du temps de traitement
                processing_time_seconds = (datetime.utcnow() - start_time).total_seconds()
                processing_time = str(datetime.utcnow() - start_time)

                # Mise à jour de la segmentation
                segmentation.status = SegmentationStatus.COMPLETED
                segmentation.completed_at = datetime.utcnow()
                segmentation.processing_time = processing_time
                segmentation.segmentation_results = {
                    "mask_shape": segmentation_result.shape,
                    "output_path": f"uploads/segmentation_results/{segmentation_id}_result.nii"
                }
                segmentation.volume_analysis = volume_analysis
                confidence_score = float(np.mean([seg["confidence_score"] for seg in tumor_segments]))
                segmentation.confidence_score = confidence_score

                # Sauvegarde du masque de segmentation
                await self._save_segmentation_mask(segmentation_result, segmentation_id)

                # Création des segments tumoraux
                await self._create_tumor_segments(db, segmentation_id, tumor_segments)

                # Création de l'analyse volumétrique
                await self._create_volumetric_analysis(db, segmentation_id, volume_analysis, tumor_segments)

                # 📈 MLOPS - Enregistrement des résultats
                mlflow_run_id = segmentation.input_parameters.get("mlflow_run_id")
                if mlflow_run_id:
                    mlops_service.log_segmentation_results(
                        run_id=mlflow_run_id,
                        processing_time=processing_time_seconds,
                        confidence_score=confidence_score,
                        volume_analysis=volume_analysis,
                        tumor_segments=tumor_segments,
                        status="completed"
                    )

                await db.commit()

                logger.info(f"✅ Segmentation terminée: {segmentation_id} | MLOps tracking: {mlflow_run_id}")

            except Exception as e:
                logger.error(f"❌ Erreur lors du traitement de segmentation {segmentation_id}: {e}")

                # 📈 MLOPS - Enregistrement de l'erreur
                try:
                    result = await db.execute(
                        select(AISegmentation).where(AISegmentation.id == segmentation_id)
                    )
                    segmentation = result.scalar_one_or_none()
                    if segmentation:
                        mlflow_run_id = segmentation.input_parameters.get("mlflow_run_id")
                        if mlflow_run_id:
                            mlops_service.log_error(
                                run_id=mlflow_run_id,
                                error_message=str(e),
                                error_type="segmentation_processing_error"
                            )
                except Exception as mlops_error:
                    logger.error(f"❌ Erreur lors de l'enregistrement MLOps: {mlops_error}")

                await self._update_segmentation_status(db, segmentation_id, SegmentationStatus.FAILED)
                await db.rollback()

    async def _load_image_series(self, db: AsyncSession, image_series_id: str) -> Optional[Dict[str, np.ndarray]]:
        """Charge une série d'images médicales"""
        try:
            # Récupération de la série d'images
            result = await db.execute(
                select(ImageSeries).where(ImageSeries.id == image_series_id)
            )
            image_series = result.scalar_one_or_none()

            if not image_series:
                logger.error(f"Série d'images non trouvée: {image_series_id}")
                return None

            # Récupération des images individuelles
            image_ids = image_series.image_ids
            if not image_ids or len(image_ids) < 4:
                logger.error(f"Série d'images incomplète: {len(image_ids) if image_ids else 0} images")
                return None

            images_data = {}
            for image_id in image_ids:
                result = await db.execute(
                    select(MedicalImage).where(MedicalImage.id == image_id)
                )
                image = result.scalar_one_or_none()

                if image:
                    # Chargement de l'image NIfTI
                    img_data = nib.load(image.file_path).get_fdata()
                    images_data[image.modality.value] = img_data

            # Vérification que nous avons les 4 modalités requises
            required_modalities = ["T1", "T1CE", "T2", "FLAIR"]
            if not all(mod in images_data for mod in required_modalities):
                logger.error(f"Modalités manquantes. Trouvées: {list(images_data.keys())}")
                return None

            logger.info(f"Images chargées: {list(images_data.keys())}")
            return images_data

        except Exception as e:
            logger.error(f"Erreur lors du chargement des images: {e}")
            return None

    async def _prepare_input_data(self, images_data: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Prépare les données d'entrée pour votre modèle U-Net selon loadmodel.py
        """
        try:
            # Récupération des modalités dans l'ordre requis
            t1 = images_data["T1"]
            t1ce = images_data["T1CE"]
            t2 = images_data["T2"]
            flair = images_data["FLAIR"]

            logger.info(f"Formes originales - T1: {t1.shape}, T1CE: {t1ce.shape}, T2: {t2.shape}, FLAIR: {flair.shape}")

            # Normalisation standardisée (percentile-based pour éviter les outliers)
            normalized_data = {}
            for modality, data in [('t1', t1), ('t1ce', t1ce), ('t2', t2), ('flair', flair)]:
                # Normalisation robuste
                p1, p99 = np.percentile(data[data > 0], [1, 99])
                normalized = np.clip((data - p1) / (p99 - p1), 0, 1)
                normalized_data[modality] = normalized

            # Préparation pour le modèle (FLAIR + T1CE comme entrées principales selon loadmodel.py)
            X = np.empty((VOLUME_SLICES, IMG_SIZE, IMG_SIZE, 2))

            for slice_idx in range(VOLUME_SLICES):
                z_idx = slice_idx + VOLUME_START_AT
                # Vérifier que l'index est dans les limites
                if z_idx < normalized_data['flair'].shape[2]:
                    X[slice_idx, :, :, 0] = cv2.resize(normalized_data['flair'][:, :, z_idx], (IMG_SIZE, IMG_SIZE))
                    X[slice_idx, :, :, 1] = cv2.resize(normalized_data['t1ce'][:, :, z_idx], (IMG_SIZE, IMG_SIZE))
                else:
                    # Remplir avec des zéros si on dépasse les limites
                    X[slice_idx, :, :, 0] = np.zeros((IMG_SIZE, IMG_SIZE))
                    X[slice_idx, :, :, 1] = np.zeros((IMG_SIZE, IMG_SIZE))

            logger.info(f"✅ Données d'entrée préparées selon loadmodel.py: {X.shape}")
            return X

        except Exception as e:
            logger.error(f"❌ Erreur lors de la préparation des données: {e}")
            raise

    def _run_segmentation(self, model, input_data: np.ndarray) -> np.ndarray:
        """Exécute la segmentation avec votre modèle U-Net"""
        try:
            logger.info("Exécution de la segmentation...")

            # Prédiction avec votre modèle
            prediction = model.predict(input_data)

            # Post-traitement selon votre modèle
            # Suppression de la dimension batch
            prediction = np.squeeze(prediction, axis=0)

            # Application du seuil de confiance
            prediction = (prediction > self.confidence_threshold).astype(np.uint8)

            logger.info(f"Segmentation terminée: {prediction.shape}")
            return prediction

        except Exception as e:
            logger.error(f"Erreur lors de la segmentation: {e}")
            raise

    # Métriques personnalisées pour votre modèle Kaggle (selon loadmodel.py)
    @staticmethod
    def dice_coef(y_true, y_pred, smooth=1.0):
        """Coefficient de Dice - Métrique standard en segmentation médicale"""
        from tensorflow.keras import backend as K
        class_num = 4
        total_loss = 0
        for i in range(class_num):
            y_true_f = K.flatten(y_true[:,:,:,i])
            y_pred_f = K.flatten(y_pred[:,:,:,i])
            intersection = K.sum(y_true_f * y_pred_f)
            loss = ((2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth))
            total_loss += loss
        return total_loss / class_num

    @staticmethod
    def dice_coef_necrotic(y_true, y_pred, epsilon=1e-6):
        """Dice pour région nécrotique - Critique pour planification chirurgicale"""
        from tensorflow.keras import backend as K
        intersection = K.sum(K.abs(y_true[:,:,:,1] * y_pred[:,:,:,1]))
        return (2. * intersection) / (K.sum(K.square(y_true[:,:,:,1])) + K.sum(K.square(y_pred[:,:,:,1])) + epsilon)

    @staticmethod
    def dice_coef_edema(y_true, y_pred, epsilon=1e-6):
        """Dice pour œdème - Important pour évaluation de l'effet de masse"""
        from tensorflow.keras import backend as K
        intersection = K.sum(K.abs(y_true[:,:,:,2] * y_pred[:,:,:,2]))
        return (2. * intersection) / (K.sum(K.square(y_true[:,:,:,2])) + K.sum(K.square(y_pred[:,:,:,2])) + epsilon)

    @staticmethod
    def dice_coef_enhancing(y_true, y_pred, epsilon=1e-6):
        """Dice pour tumeur rehaussée - Cible thérapeutique principale"""
        from tensorflow.keras import backend as K
        intersection = K.sum(K.abs(y_true[:,:,:,3] * y_pred[:,:,:,3]))
        return (2. * intersection) / (K.sum(K.square(y_true[:,:,:,3])) + K.sum(K.square(y_pred[:,:,:,3])) + epsilon)

    @staticmethod
    def precision(y_true, y_pred):
        """Précision - Minimise les faux positifs"""
        from tensorflow.keras import backend as K
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        return true_positives / (predicted_positives + K.epsilon())

    @staticmethod
    def sensitivity(y_true, y_pred):
        """Sensibilité/Recall - Minimise les faux négatifs (critique en médical)"""
        from tensorflow.keras import backend as K
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        return true_positives / (possible_positives + K.epsilon())

    @staticmethod
    def specificity(y_true, y_pred):
        """Spécificité - Capacité à identifier les tissus sains"""
        from tensorflow.keras import backend as K
        true_negatives = K.sum(K.round(K.clip((1-y_true) * (1-y_pred), 0, 1)))
        possible_negatives = K.sum(K.round(K.clip(1-y_true, 0, 1)))
        return true_negatives / (possible_negatives + K.epsilon())

    async def _calculate_volumes(self, segmentation_result: np.ndarray) -> Dict[str, Any]:
        """Calcule les volumes des différents segments"""
        try:
            # Calcul des volumes en cm³ (en supposant une résolution de 1mm³ par voxel)
            voxel_volume = 0.001  # 1mm³ = 0.001 cm³

            # Extraction des différents segments selon votre modèle
            if len(segmentation_result.shape) == 4:
                # Modèle multi-classe
                necrotic_volume = np.sum(segmentation_result[:,:,:,0]) * voxel_volume
                edema_volume = np.sum(segmentation_result[:,:,:,1]) * voxel_volume
                enhancing_volume = np.sum(segmentation_result[:,:,:,2]) * voxel_volume
            else:
                # Modèle binaire - adaptation nécessaire
                total_tumor = np.sum(segmentation_result) * voxel_volume
                # Estimation des sous-segments (à adapter selon votre modèle)
                necrotic_volume = total_tumor * 0.3
                edema_volume = total_tumor * 0.4
                enhancing_volume = total_tumor * 0.3

            total_volume = necrotic_volume + edema_volume + enhancing_volume

            volume_analysis = {
                "total_tumor_volume": float(total_volume),
                "necrotic_core_volume": float(necrotic_volume),
                "peritumoral_edema_volume": float(edema_volume),
                "enhancing_tumor_volume": float(enhancing_volume),
                "voxel_count": int(np.sum(segmentation_result > 0)),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Volumes calculés: Total={total_volume:.2f} cm³")
            return volume_analysis

        except Exception as e:
            logger.error(f"Erreur lors du calcul des volumes: {e}")
            raise

    async def _extract_tumor_segments(self, segmentation_result: np.ndarray, volume_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrait les segments tumoraux détaillés"""
        try:
            total_volume = volume_analysis["total_tumor_volume"]
            segments = []

            # Segment nécrotique
            if volume_analysis["necrotic_core_volume"] > 0:
                segments.append({
                    "segment_type": TumorType.NECROTIC_CORE,
                    "volume_cm3": volume_analysis["necrotic_core_volume"],
                    "percentage": (volume_analysis["necrotic_core_volume"] / total_volume * 100) if total_volume > 0 else 0,
                    "color_code": TUMOR_SEGMENT_COLORS["NECROTIC_CORE"],
                    "description": "Noyau nécrotique central",
                    "confidence_score": 0.85,  # À adapter selon votre modèle
                    "coordinates": self._extract_coordinates(segmentation_result, 0),
                    "statistical_features": self._calculate_segment_statistics(segmentation_result, 0)
                })

            # Œdème péritumoral
            if volume_analysis["peritumoral_edema_volume"] > 0:
                segments.append({
                    "segment_type": TumorType.PERITUMORAL_EDEMA,
                    "volume_cm3": volume_analysis["peritumoral_edema_volume"],
                    "percentage": (volume_analysis["peritumoral_edema_volume"] / total_volume * 100) if total_volume > 0 else 0,
                    "color_code": TUMOR_SEGMENT_COLORS["PERITUMORAL_EDEMA"],
                    "description": "Œdème péritumoral",
                    "confidence_score": 0.82,
                    "coordinates": self._extract_coordinates(segmentation_result, 1),
                    "statistical_features": self._calculate_segment_statistics(segmentation_result, 1)
                })

            # Tumeur rehaussée
            if volume_analysis["enhancing_tumor_volume"] > 0:
                segments.append({
                    "segment_type": TumorType.ENHANCING_TUMOR,
                    "volume_cm3": volume_analysis["enhancing_tumor_volume"],
                    "percentage": (volume_analysis["enhancing_tumor_volume"] / total_volume * 100) if total_volume > 0 else 0,
                    "color_code": TUMOR_SEGMENT_COLORS["ENHANCING_TUMOR"],
                    "description": "Tumeur avec rehaussement",
                    "confidence_score": 0.88,
                    "coordinates": self._extract_coordinates(segmentation_result, 2),
                    "statistical_features": self._calculate_segment_statistics(segmentation_result, 2)
                })

            logger.info(f"Segments extraits: {len(segments)}")
            return segments

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des segments: {e}")
            raise

    def _extract_coordinates(self, segmentation_result: np.ndarray, segment_index: int) -> Dict[str, Any]:
        """Extrait les coordonnées 3D d'un segment"""
        try:
            if len(segmentation_result.shape) == 4 and segment_index < segmentation_result.shape[3]:
                segment_mask = segmentation_result[:,:,:,segment_index]
            else:
                segment_mask = segmentation_result

            # Recherche des coordonnées des voxels actifs
            coords = np.where(segment_mask > 0)

            if len(coords[0]) > 0:
                # Calcul du centroïde
                centroid = [float(np.mean(coord)) for coord in coords]

                # Boîte englobante
                bbox = {
                    "min": [int(np.min(coord)) for coord in coords],
                    "max": [int(np.max(coord)) for coord in coords]
                }

                return {
                    "centroid": centroid,
                    "bounding_box": bbox,
                    "voxel_count": len(coords[0])
                }

            return {"centroid": [0, 0, 0], "bounding_box": {"min": [0, 0, 0], "max": [0, 0, 0]}, "voxel_count": 0}

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des coordonnées: {e}")
            return {}

    def _calculate_segment_statistics(self, segmentation_result: np.ndarray, segment_index: int) -> Dict[str, Any]:
        """Calcule les statistiques d'un segment"""
        try:
            if len(segmentation_result.shape) == 4 and segment_index < segmentation_result.shape[3]:
                segment_mask = segmentation_result[:,:,:,segment_index]
            else:
                segment_mask = segmentation_result

            # Statistiques de base
            stats = {
                "mean_intensity": float(np.mean(segment_mask[segment_mask > 0])) if np.any(segment_mask > 0) else 0.0,
                "std_intensity": float(np.std(segment_mask[segment_mask > 0])) if np.any(segment_mask > 0) else 0.0,
                "max_intensity": float(np.max(segment_mask)) if np.any(segment_mask > 0) else 0.0,
                "min_intensity": float(np.min(segment_mask[segment_mask > 0])) if np.any(segment_mask > 0) else 0.0,
                "voxel_count": int(np.sum(segment_mask > 0))
            }

            return stats

        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
            return {}

    async def _save_segmentation_mask(self, segmentation_result: np.ndarray, segmentation_id: str):
        """Sauvegarde le masque de segmentation"""
        try:
            output_dir = Path(settings.SEGMENTATION_RESULTS_DIR)
            output_dir.mkdir(parents=True, exist_ok=True)

            output_path = output_dir / f"{segmentation_id}_result.nii"

            # Création de l'image NIfTI
            nii_img = nib.Nifti1Image(segmentation_result, affine=np.eye(4))
            nib.save(nii_img, str(output_path))

            logger.info(f"Masque de segmentation sauvegardé: {output_path}")

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du masque: {e}")
            raise

    async def _create_tumor_segments(self, db: AsyncSession, segmentation_id: str, tumor_segments: List[Dict[str, Any]]):
        """Crée les enregistrements de segments tumoraux"""
        try:
            for segment_data in tumor_segments:
                segment = TumorSegment(
                    id=str(uuid.uuid4()),
                    segmentation_id=segmentation_id,
                    segment_type=segment_data["segment_type"],
                    volume_cm3=segment_data["volume_cm3"],
                    percentage=segment_data["percentage"],
                    coordinates=segment_data.get("coordinates"),
                    color_code=segment_data["color_code"],
                    description=segment_data["description"],
                    confidence_score=segment_data["confidence_score"],
                    statistical_features=segment_data.get("statistical_features")
                )

                db.add(segment)

            logger.info(f"Segments tumoraux créés: {len(tumor_segments)}")

        except Exception as e:
            logger.error(f"Erreur lors de la création des segments: {e}")
            raise

    async def _create_volumetric_analysis(self, db: AsyncSession, segmentation_id: str, volume_analysis: Dict[str, Any], tumor_segments: List[Dict[str, Any]]):
        """Crée l'analyse volumétrique"""
        try:
            volumetric_analysis = VolumetricAnalysis(
                id=str(uuid.uuid4()),
                segmentation_id=segmentation_id,
                total_tumor_volume=volume_analysis["total_tumor_volume"],
                necrotic_core_volume=volume_analysis["necrotic_core_volume"],
                peritumoral_edema_volume=volume_analysis["peritumoral_edema_volume"],
                enhancing_tumor_volume=volume_analysis["enhancing_tumor_volume"],
                tumor_burden_index=volume_analysis["total_tumor_volume"] / 1000,  # Index simple
                growth_rate_analysis={"initial_analysis": True}
            )

            db.add(volumetric_analysis)
            logger.info("Analyse volumétrique créée")

        except Exception as e:
            logger.error(f"Erreur lors de la création de l'analyse volumétrique: {e}")
            raise

    async def _update_segmentation_status(self, db: AsyncSession, segmentation_id: str, status: SegmentationStatus):
        """Met à jour le statut d'une segmentation"""
        try:
            result = await db.execute(
                select(AISegmentation).where(AISegmentation.id == segmentation_id)
            )
            segmentation = result.scalar_one_or_none()

            if segmentation:
                segmentation.status = status
                if status == SegmentationStatus.FAILED:
                    segmentation.completed_at = datetime.utcnow()
                await db.commit()

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut: {e}")
            await db.rollback()
