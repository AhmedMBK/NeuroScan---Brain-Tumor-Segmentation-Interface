"""
🧠 CereBloom - Service MLOps Minimal
Tracking, Monitoring et Dashboard automatique pour segmentation de tumeurs cérébrales
"""

import os
import time
import uuid
import mlflow
import mlflow.sklearn
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import json
import numpy as np
from pathlib import Path

from config.settings import settings

logger = logging.getLogger(__name__)

class MLOpsService:
    """Service MLOps minimal pour CereBloom - Tracking automatique des segmentations"""
    
    def __init__(self):
        self.experiment_name = "cerebloom_brain_tumor_segmentation"
        self.model_name = "unet_brain_tumor_model"
        self.tracking_uri = "file:./mlruns"  # Local storage
        self.setup_mlflow()
        
    def setup_mlflow(self):
        """Configuration initiale de MLflow"""
        try:
            # Configuration du tracking URI
            mlflow.set_tracking_uri(self.tracking_uri)
            
            # Création ou récupération de l'expérience
            try:
                experiment = mlflow.get_experiment_by_name(self.experiment_name)
                if experiment is None:
                    experiment_id = mlflow.create_experiment(
                        self.experiment_name,
                        tags={
                            "project": "CereBloom",
                            "model_type": "U-Net",
                            "domain": "Medical_Imaging",
                            "task": "Brain_Tumor_Segmentation"
                        }
                    )
                    logger.info(f"✅ Expérience MLflow créée: {self.experiment_name}")
                else:
                    experiment_id = experiment.experiment_id
                    logger.info(f"✅ Expérience MLflow trouvée: {self.experiment_name}")
                    
                mlflow.set_experiment(self.experiment_name)
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la configuration de l'expérience: {e}")
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la configuration MLflow: {e}")
    
    def start_segmentation_run(self, 
                             patient_id: str, 
                             doctor_id: str, 
                             image_series_id: str,
                             input_parameters: Dict[str, Any] = None) -> str:
        """
        Démarre un run MLflow pour une nouvelle segmentation
        
        Returns:
            run_id: Identifiant unique du run MLflow
        """
        try:
            logger.info(f"🔍 MLOPS DEBUG - Démarrage run pour patient: {patient_id}")

            # Démarrage du run MLflow
            run = mlflow.start_run(
                run_name=f"segmentation_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            run_id = run.info.run_id
            logger.info(f"🔍 MLOPS DEBUG - Run ID créé: {run_id}")
            
            # 📊 TRACKING AUTOMATIQUE - Paramètres d'entrée
            mlflow.log_params({
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "image_series_id": image_series_id,
                "model_version": settings.AI_MODEL_VERSION,
                "confidence_threshold": settings.AI_CONFIDENCE_THRESHOLD,
                "processing_date": datetime.now().isoformat(),
                "input_parameters": json.dumps(input_parameters or {})
            })
            
            # Tags pour organisation
            mlflow.set_tags({
                "stage": "production",
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "model_type": "U-Net",
                "medical_domain": "neurology"
            })
            
            logger.info(f"✅ Run MLflow démarré: {run_id}")

            # NE PAS fermer le run ici - le laisser ouvert pour les métriques
            # mlflow.end_run()  # Commenté pour permettre l'ajout de métriques

            return run_id
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du démarrage du run MLflow: {e}")
            return None
    
    def log_segmentation_results(self,
                               run_id: str,
                               processing_time: float,
                               confidence_score: float,
                               volume_analysis: Dict[str, Any],
                               tumor_segments: List[Dict[str, Any]],
                               status: str = "completed") -> None:
        """
        Enregistre les résultats de segmentation dans MLflow
        """
        try:
            logger.info(f"🔍 MLOPS DEBUG - Enregistrement résultats pour run: {run_id}")
            logger.info(f"🔍 MLOPS DEBUG - Volume analysis: {volume_analysis}")
            logger.info(f"🔍 MLOPS DEBUG - Tumor segments: {tumor_segments}")

            # Approche simplifiée : utiliser le run actif ou le reprendre
            current_run = mlflow.active_run()
            if current_run and current_run.info.run_id == run_id:
                # Le run est déjà actif, utiliser directement
                logger.info(f"🔍 Run déjà actif: {run_id}")
                self._log_metrics_and_data(volume_analysis, tumor_segments, processing_time, confidence_score, status)
            else:
                # Reprendre le run spécifique
                logger.info(f"🔍 Reprise du run: {run_id}")
                with mlflow.start_run(run_id=run_id):
                    self._log_metrics_and_data(volume_analysis, tumor_segments, processing_time, confidence_score, status)

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'enregistrement des résultats: {e}")

    def finalize_run(self, run_id: str):
        """Finalise et ferme le run MLflow"""
        try:
            current_run = mlflow.active_run()
            if current_run and current_run.info.run_id == run_id:
                mlflow.end_run()
                logger.info(f"✅ Run MLflow finalisé: {run_id}")
            else:
                logger.info(f"ℹ️ Run déjà fermé ou non actif: {run_id}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la finalisation du run: {e}")

    def _log_metrics_and_data(self, volume_analysis, tumor_segments, processing_time, confidence_score, status):
        """Méthode helper pour enregistrer les métriques"""
        # 📈 MONITORING CONTINU - Métriques de performance
        # Extraction des volumes depuis tumor_segments
        necrotic_volume = 0
        edema_volume = 0
        enhancing_volume = 0

        for segment in tumor_segments:
            if segment.get("type") == "NECROTIC_CORE":
                necrotic_volume = segment.get("volume_cm3", 0)
            elif segment.get("type") == "PERITUMORAL_EDEMA":
                edema_volume = segment.get("volume_cm3", 0)
            elif segment.get("type") == "ENHANCING_TUMOR":
                enhancing_volume = segment.get("volume_cm3", 0)

        mlflow.log_metrics({
            "processing_time_seconds": processing_time,
            "confidence_score": confidence_score,
            "total_tumor_volume_cm3": volume_analysis.get("total_volume_cm3", 0),
            "necrotic_volume_cm3": necrotic_volume,
            "edema_volume_cm3": edema_volume,
            "enhancing_volume_cm3": enhancing_volume,
            "number_of_segments": len(tumor_segments),
            "timestamp": time.time()
        })

        # Métriques de qualité
        if tumor_segments:
            avg_segment_confidence = np.mean([seg.get("confidence_score", 0) for seg in tumor_segments])
            mlflow.log_metric("average_segment_confidence", avg_segment_confidence)

        # Statut de la segmentation
        mlflow.log_param("segmentation_status", status)

        # Sauvegarde des résultats détaillés (version optimisée)
        try:
            mlflow.log_dict(volume_analysis, "volume_analysis.json")
            mlflow.log_dict(tumor_segments, "tumor_segments.json")
        except Exception as save_error:
            logger.warning(f"⚠️ Erreur sauvegarde fichiers MLflow (non critique): {save_error}")
            # Continuer sans bloquer - les métriques principales sont déjà sauvées

        logger.info(f"✅ Résultats enregistrés dans MLflow")

    def log_error(self, run_id: str, error_message: str, error_type: str = "processing_error"):
        """Enregistre les erreurs dans MLflow"""
        try:
            with mlflow.start_run(run_id=run_id):
                mlflow.log_param("segmentation_status", "failed")
                mlflow.log_param("error_type", error_type)
                mlflow.log_param("error_message", error_message)
                mlflow.log_metric("processing_time_seconds", 0)
                mlflow.log_metric("confidence_score", 0)
                
                logger.info(f"✅ Erreur enregistrée dans MLflow: {run_id}")
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'enregistrement de l'erreur: {e}")
    
    def get_daily_statistics(self, date: datetime = None) -> Dict[str, Any]:
        """Récupère les statistiques quotidiennes pour le monitoring"""
        try:
            if date is None:
                date = datetime.now()
            
            # Recherche des runs du jour
            start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
            
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                return {"error": "Expérience non trouvée"}
            
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=f"attribute.start_time >= '{start_time.isoformat()}' AND attribute.start_time < '{end_time.isoformat()}'",
                order_by=["start_time DESC"]
            )
            
            if runs.empty:
                return {
                    "date": date.strftime("%Y-%m-%d"),
                    "total_segmentations": 0,
                    "successful_segmentations": 0,
                    "failed_segmentations": 0,
                    "average_processing_time": 0,
                    "average_confidence": 0,
                    "total_volume_processed": 0
                }
            
            # Calcul des statistiques
            successful_runs = runs[runs['params.segmentation_status'] == 'completed']
            failed_runs = runs[runs['params.segmentation_status'] == 'failed']
            
            stats = {
                "date": date.strftime("%Y-%m-%d"),
                "total_segmentations": len(runs),
                "successful_segmentations": len(successful_runs),
                "failed_segmentations": len(failed_runs),
                "success_rate": (len(successful_runs) / len(runs) * 100) if len(runs) > 0 else 0,
                "average_processing_time": successful_runs['metrics.processing_time_seconds'].mean() if not successful_runs.empty else 0,
                "average_confidence": successful_runs['metrics.confidence_score'].mean() if not successful_runs.empty else 0,
                "total_volume_processed": successful_runs['metrics.total_tumor_volume_cm3'].sum() if not successful_runs.empty else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul des statistiques: {e}")
            return {"error": str(e)}
    
    def get_model_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """Analyse des tendances de performance sur plusieurs jours"""
        try:
            trends = []
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                daily_stats = self.get_daily_statistics(date)
                trends.append(daily_stats)
            
            return {
                "period_days": days,
                "daily_trends": trends,
                "summary": {
                    "total_segmentations": sum(day.get("total_segmentations", 0) for day in trends),
                    "average_success_rate": np.mean([day.get("success_rate", 0) for day in trends if "error" not in day]),
                    "average_processing_time": np.mean([day.get("average_processing_time", 0) for day in trends if "error" not in day]),
                    "average_confidence": np.mean([day.get("average_confidence", 0) for day in trends if "error" not in day])
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des tendances: {e}")
            return {"error": str(e)}
    
    def get_dashboard_url(self) -> str:
        """Retourne l'URL du dashboard MLflow"""
        return "http://localhost:5000"
    
    def start_mlflow_server(self):
        """Démarre le serveur MLflow UI (à appeler au démarrage de l'application)"""
        try:
            import subprocess
            import threading
            
            def run_mlflow_ui():
                subprocess.run([
                    "mlflow", "ui", 
                    "--backend-store-uri", self.tracking_uri,
                    "--host", "0.0.0.0",
                    "--port", "5000"
                ], check=False)
            
            # Démarrage en arrière-plan
            thread = threading.Thread(target=run_mlflow_ui, daemon=True)
            thread.start()
            
            logger.info("✅ Serveur MLflow UI démarré sur http://localhost:5000")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du démarrage du serveur MLflow: {e}")

# Instance globale du service MLOps
mlops_service = MLOpsService()
