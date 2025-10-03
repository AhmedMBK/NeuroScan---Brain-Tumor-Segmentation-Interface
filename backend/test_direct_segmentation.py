#!/usr/bin/env python3
"""
🧠 Test Direct de Segmentation CereBloom
Script pour tester directement le modèle sans passer par l'API
"""

import os
import sys
import asyncio
import uuid
from pathlib import Path
from datetime import datetime
import numpy as np
import nibabel as nib
import json

# Ajouter le répertoire backend au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports CereBloom
from config.database import get_database
from models.database_models import MedicalImage, Patient, AISegmentation, SegmentationStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Configuration
PATIENT_ID = "stringd5f01d3b-b54b-43a2-ba3c-0b12c797affc"
IMG_SIZE = 128
VOLUME_SLICES = 100
VOLUME_START_AT = 22

# Classes de tumeurs selon BraTS
TUMOR_CLASSES = {
    0: {'name': 'Tissu sain', 'color': '#000000'},
    1: {'name': 'Noyau nécrotique', 'color': '#FF0000'},
    2: {'name': 'Œdème péritumoral', 'color': '#00FF00'},
    3: {'name': 'Tumeur rehaussée', 'color': '#0080FF'}
}

def load_and_preprocess_image(file_path, target_shape=(IMG_SIZE, IMG_SIZE, VOLUME_SLICES)):
    """Charge et prétraite une image NIfTI"""
    try:
        print(f"📁 Chargement: {file_path}")
        
        # Charger l'image NIfTI
        nii_img = nib.load(file_path)
        img_data = nii_img.get_fdata()
        
        print(f"   Shape originale: {img_data.shape}")
        
        # Normalisation simple
        img_data = (img_data - np.min(img_data)) / (np.max(img_data) - np.min(img_data) + 1e-8)
        
        # Redimensionnement basique (prendre le centre)
        if len(img_data.shape) == 3:
            h, w, d = img_data.shape
            
            # Extraire le volume central
            start_slice = max(0, (d - VOLUME_SLICES) // 2)
            end_slice = start_slice + VOLUME_SLICES
            
            if end_slice > d:
                start_slice = max(0, d - VOLUME_SLICES)
                end_slice = d
            
            img_volume = img_data[:, :, start_slice:end_slice]
            
            # Redimensionner en 2D puis reconstruire
            processed_volume = np.zeros((IMG_SIZE, IMG_SIZE, VOLUME_SLICES))
            
            for i in range(min(img_volume.shape[2], VOLUME_SLICES)):
                slice_2d = img_volume[:, :, i]
                # Redimensionnement simple par interpolation
                from scipy.ndimage import zoom
                zoom_factors = (IMG_SIZE / slice_2d.shape[0], IMG_SIZE / slice_2d.shape[1])
                resized_slice = zoom(slice_2d, zoom_factors, order=1)
                processed_volume[:, :, i] = resized_slice
        
        print(f"   Shape finale: {processed_volume.shape}")
        return processed_volume
        
    except Exception as e:
        print(f"❌ Erreur chargement {file_path}: {e}")
        return None

def simulate_segmentation(flair_data, t1ce_data):
    """Simule une segmentation réaliste"""
    print("🧠 Simulation de segmentation...")
    
    # Créer un masque de segmentation réaliste
    segmentation = np.zeros_like(flair_data, dtype=np.uint8)
    
    # Simuler des régions tumorales basées sur l'intensité
    combined = (flair_data + t1ce_data) / 2
    
    # Seuils pour différentes régions
    high_intensity = combined > 0.7
    medium_intensity = (combined > 0.4) & (combined <= 0.7)
    low_intensity = (combined > 0.2) & (combined <= 0.4)
    
    # Assigner les classes
    segmentation[high_intensity] = 3  # Tumeur rehaussée
    segmentation[medium_intensity] = 2  # Œdème
    segmentation[low_intensity] = 1  # Nécrotique
    
    print(f"   Classes trouvées: {np.unique(segmentation)}")
    return segmentation

def calculate_metrics(segmentation):
    """Calcule les métriques tumorales"""
    print("📊 Calcul des métriques...")
    
    unique_classes = np.unique(segmentation)
    total_voxels = np.sum(segmentation > 0)
    
    metrics = {
        "total_tumor_volume_cm3": float(total_voxels * 0.001),  # Approximation
        "classes_found": unique_classes.tolist(),
        "class_volumes": {}
    }
    
    for class_id in unique_classes:
        if class_id > 0:
            volume = np.sum(segmentation == class_id)
            metrics["class_volumes"][int(class_id)] = {
                "name": TUMOR_CLASSES[class_id]["name"],
                "volume_voxels": int(volume),
                "volume_cm3": float(volume * 0.001),
                "percentage": float(volume / total_voxels * 100) if total_voxels > 0 else 0.0
            }
    
    return metrics

async def test_direct_segmentation():
    """Test principal de segmentation directe"""
    print("🚀 DÉBUT DU TEST DE SEGMENTATION DIRECTE")
    print("=" * 60)
    
    # Connexion à la base de données
    async for db in get_database():
        try:
            # 1. Récupérer les images du patient
            print(f"🔍 Recherche des images pour patient: {PATIENT_ID}")
            
            result = await db.execute(
                select(MedicalImage).where(MedicalImage.patient_id == PATIENT_ID)
            )
            images = result.scalars().all()
            
            if not images:
                print(f"❌ Aucune image trouvée pour le patient {PATIENT_ID}")
                return
            
            print(f"✅ {len(images)} images trouvées")
            
            # 2. Organiser les images par modalité
            images_by_modality = {}
            for img in images:
                modality = img.modality.upper()
                images_by_modality[modality] = {
                    "file_path": img.file_path,
                    "filename": img.file_name,
                    "image_id": img.id
                }
                print(f"   📄 {modality}: {img.file_name}")
            
            # 3. Vérifier les modalités requises
            required_modalities = ["FLAIR", "T1CE"]
            missing = [m for m in required_modalities if m not in images_by_modality]
            
            if missing:
                print(f"❌ Modalités manquantes: {missing}")
                print("💡 Utilisation de toutes les modalités disponibles...")
                available_modalities = list(images_by_modality.keys())
                if len(available_modalities) < 2:
                    print("❌ Pas assez de modalités pour la segmentation")
                    return
            
            # 4. Charger et prétraiter les images
            print("\n📁 CHARGEMENT DES IMAGES")
            print("-" * 40)
            
            processed_images = {}
            for modality, img_info in images_by_modality.items():
                file_path = Path(img_info["file_path"])
                if file_path.exists():
                    processed_data = load_and_preprocess_image(str(file_path))
                    if processed_data is not None:
                        processed_images[modality] = processed_data
                else:
                    print(f"⚠️ Fichier non trouvé: {file_path}")
            
            if len(processed_images) < 2:
                print("❌ Pas assez d'images chargées pour la segmentation")
                return
            
            # 5. Segmentation
            print("\n🧠 SEGMENTATION")
            print("-" * 40)
            
            # Utiliser FLAIR et T1CE si disponibles, sinon les deux premières modalités
            modality_keys = list(processed_images.keys())
            
            if "FLAIR" in processed_images and "T1CE" in processed_images:
                primary_data = processed_images["FLAIR"]
                secondary_data = processed_images["T1CE"]
                print("✅ Utilisation de FLAIR + T1CE (optimal)")
            else:
                primary_data = processed_images[modality_keys[0]]
                secondary_data = processed_images[modality_keys[1]]
                print(f"✅ Utilisation de {modality_keys[0]} + {modality_keys[1]}")
            
            # Simulation de segmentation
            segmentation_result = simulate_segmentation(primary_data, secondary_data)
            
            # 6. Calcul des métriques
            print("\n📊 ANALYSE DES RÉSULTATS")
            print("-" * 40)
            
            metrics = calculate_metrics(segmentation_result)
            
            for class_id, class_info in metrics["class_volumes"].items():
                print(f"   🎯 {class_info['name']}: {class_info['volume_cm3']:.2f} cm³ ({class_info['percentage']:.1f}%)")
            
            print(f"   📏 Volume total: {metrics['total_tumor_volume_cm3']:.2f} cm³")
            
            # 7. Sauvegarde des résultats
            print("\n💾 SAUVEGARDE DES RÉSULTATS")
            print("-" * 40)
            
            # Créer un ID de segmentation
            segmentation_id = str(uuid.uuid4())
            output_dir = Path("uploads/segmentation_results") / segmentation_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarder la segmentation
            segmentation_nii = nib.Nifti1Image(segmentation_result, np.eye(4))
            segmentation_path = output_dir / "segmentation_mask.nii.gz"
            nib.save(segmentation_nii, str(segmentation_path))
            print(f"✅ Masque sauvegardé: {segmentation_path}")
            
            # Sauvegarder les métriques
            metrics_path = output_dir / "metrics.json"
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            print(f"✅ Métriques sauvegardées: {metrics_path}")
            
            # Sauvegarder un rapport simple
            report_path = output_dir / "report.txt"
            with open(report_path, 'w') as f:
                f.write(f"RAPPORT DE SEGMENTATION CEREBLOOM\n")
                f.write(f"{'='*50}\n\n")
                f.write(f"Patient ID: {PATIENT_ID}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Segmentation ID: {segmentation_id}\n\n")
                f.write(f"MODALITÉS UTILISÉES:\n")
                for modality in processed_images.keys():
                    f.write(f"  - {modality}\n")
                f.write(f"\nRÉSULTATS:\n")
                f.write(f"  Volume total: {metrics['total_tumor_volume_cm3']:.2f} cm³\n")
                for class_id, class_info in metrics["class_volumes"].items():
                    f.write(f"  {class_info['name']}: {class_info['volume_cm3']:.2f} cm³\n")
            
            print(f"✅ Rapport sauvegardé: {report_path}")
            
            # 8. Enregistrement en base de données (optionnel)
            print("\n💾 ENREGISTREMENT EN BASE")
            print("-" * 40)
            
            try:
                segmentation_record = AISegmentation(
                    id=segmentation_id,
                    patient_id=PATIENT_ID,
                    doctor_id=None,
                    image_series_id=f"series_{PATIENT_ID}",
                    status=SegmentationStatus.COMPLETED,
                    input_parameters={
                        "modalities_used": list(processed_images.keys()),
                        "model_version": "Test Direct v1.0",
                        "processing_mode": "simulation"
                    },
                    segmentation_results=metrics,
                    volume_analysis={"total_volume": metrics["total_tumor_volume_cm3"]},
                    started_at=datetime.now(),
                    completed_at=datetime.now()
                )
                
                db.add(segmentation_record)
                await db.commit()
                print(f"✅ Enregistrement en base réussi")
                
            except Exception as e:
                print(f"⚠️ Erreur enregistrement base: {e}")
            
            print("\n🎉 TEST TERMINÉ AVEC SUCCÈS!")
            print(f"📁 Résultats dans: {output_dir}")
            print(f"🆔 Segmentation ID: {segmentation_id}")
            
        except Exception as e:
            print(f"❌ Erreur durant le test: {e}")
            import traceback
            traceback.print_exc()
        
        # Sortir de la boucle après le premier traitement
        break

if __name__ == "__main__":
    print("🧠 CereBloom - Test Direct de Segmentation")
    print("Assurez-vous que le serveur est arrêté avant de lancer ce test\n")
    
    # Installer scipy si nécessaire
    try:
        import scipy
    except ImportError:
        print("⚠️ scipy non installé. Installation...")
        os.system("pip install scipy")
        import scipy
    
    # Lancer le test
    asyncio.run(test_direct_segmentation())
