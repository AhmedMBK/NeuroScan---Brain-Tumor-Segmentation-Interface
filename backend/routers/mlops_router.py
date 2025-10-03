"""
🧠 CereBloom - Router MLOps
Endpoints pour monitoring et dashboard MLOps
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from services.mlops_service import mlops_service
from services.auth_service import get_current_user
from models.database_models import User, UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mlops", tags=["MLOps"])

@router.get("/dashboard-url")
async def get_dashboard_url(current_user: User = Depends(get_current_user)):
    """
    📋 Retourne l'URL du dashboard MLflow
    Accessible aux médecins et admins
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins et admins")
    
    try:
        dashboard_url = mlops_service.get_dashboard_url()
        return {
            "dashboard_url": dashboard_url,
            "description": "Dashboard MLOps - Monitoring des segmentations",
            "access_info": "Interface web pour visualiser les métriques de performance"
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'URL dashboard: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")

@router.get("/statistics/daily")
async def get_daily_statistics(
    date: Optional[str] = Query(None, description="Date au format YYYY-MM-DD"),
    current_user: User = Depends(get_current_user)
):
    """
    📊 Statistiques quotidiennes des segmentations
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins et admins")
    
    try:
        # Parse de la date si fournie
        target_date = datetime.now()
        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")
        
        stats = mlops_service.get_daily_statistics(target_date)
        
        return {
            "status": "success",
            "data": stats,
            "metadata": {
                "requested_date": target_date.strftime("%Y-%m-%d"),
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du calcul des statistiques")

@router.get("/statistics/trends")
async def get_performance_trends(
    days: int = Query(7, ge=1, le=30, description="Nombre de jours à analyser (1-30)"),
    current_user: User = Depends(get_current_user)
):
    """
    📈 Tendances de performance sur plusieurs jours
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins et admins")
    
    try:
        trends = mlops_service.get_model_performance_trends(days)
        
        return {
            "status": "success",
            "data": trends,
            "metadata": {
                "analysis_period_days": days,
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des tendances: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'analyse des tendances")

@router.get("/statistics/summary")
async def get_mlops_summary(current_user: User = Depends(get_current_user)):
    """
    📋 Résumé complet MLOps pour dashboard principal
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins et admins")
    
    try:
        # Statistiques du jour
        today_stats = mlops_service.get_daily_statistics()
        
        # Tendances sur 7 jours
        weekly_trends = mlops_service.get_model_performance_trends(7)
        
        # Calcul des métriques clés
        summary = {
            "today": today_stats,
            "weekly_summary": weekly_trends.get("summary", {}),
            "dashboard_url": mlops_service.get_dashboard_url(),
            "key_metrics": {
                "segmentations_today": today_stats.get("total_segmentations", 0),
                "success_rate_today": round(today_stats.get("success_rate", 0), 1),
                "avg_processing_time": round(today_stats.get("average_processing_time", 0), 2),
                "avg_confidence": round(today_stats.get("average_confidence", 0), 3),
                "weekly_total": weekly_trends.get("summary", {}).get("total_segmentations", 0)
            },
            "status_indicators": {
                "system_health": "healthy" if today_stats.get("success_rate", 0) > 90 else "warning",
                "performance": "good" if today_stats.get("average_processing_time", 0) < 5 else "slow",
                "confidence": "high" if today_stats.get("average_confidence", 0) > 0.8 else "medium"
            }
        }
        
        return {
            "status": "success",
            "data": summary,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "mlops_version": "minimal_v1.0"
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du résumé MLOps: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la génération du résumé")

@router.post("/start-dashboard")
async def start_mlflow_dashboard(current_user: User = Depends(get_current_user)):
    """
    🚀 Démarre le serveur MLflow UI
    Réservé aux admins
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    
    try:
        mlops_service.start_mlflow_server()
        
        return {
            "status": "success",
            "message": "Serveur MLflow UI démarré",
            "dashboard_url": mlops_service.get_dashboard_url(),
            "instructions": "Le dashboard sera accessible dans quelques secondes"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du dashboard: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du démarrage du dashboard")

@router.get("/health")
async def mlops_health_check():
    """
    ✅ Vérification de l'état du système MLOps
    Endpoint public pour monitoring
    """
    try:
        # Test basique de MLflow
        today_stats = mlops_service.get_daily_statistics()
        
        health_status = {
            "mlops_status": "operational",
            "mlflow_accessible": True,
            "last_segmentation": today_stats.get("total_segmentations", 0) > 0,
            "dashboard_url": mlops_service.get_dashboard_url(),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "healthy",
            "data": health_status
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du health check MLOps: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
