#!/usr/bin/env python3
"""
🧠 CereBloom - Backend Principal
Application de cabinet médical avec IA de segmentation de tumeurs cérébrales

Architecture basée sur le diagramme UML Relations et Flux de Données
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime
import os
from pathlib import Path

# Imports des modules CereBloom
from config.database import init_database, get_database
from config.settings import Settings
from models.database_models import *
from routers import (
    auth_router,
    users_router,
    doctors_router,
    patients_router,
    medical_images_router,
    ai_segmentation_router,  # ✅ Activé pour la segmentation IA
    treatments_router,
    appointments_router,
    reports_router,
    mlops_router  # ✅ AJOUTÉ : Router MLOps
)
from services.auth_service import AuthService
from services.mlops_service import mlops_service
from utils.logger import setup_logger

# Configuration
settings = Settings()
security = HTTPBearer()
logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    logger.info("Demarrage de CereBloom Backend...")

    # Initialisation de la base de données
    await init_database()
    logger.info("Base de donnees initialisee")

    # Création des dossiers nécessaires
    os.makedirs("uploads/medical_images", exist_ok=True)
    os.makedirs("uploads/segmentation_results", exist_ok=True)
    os.makedirs("uploads/reports", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    os.makedirs("mlruns", exist_ok=True)  # ✅ AJOUTÉ : Dossier MLflow
    logger.info("Dossiers crees")

    # 📊 MLOPS - Démarrage automatique du serveur MLflow
    try:
        mlops_service.start_mlflow_server()
        logger.info("✅ Serveur MLflow UI démarré sur http://localhost:5000")
    except Exception as e:
        logger.warning(f"⚠️ Impossible de démarrer MLflow UI: {e}")

    yield

    logger.info("Arret de CereBloom Backend...")

# Application FastAPI
app = FastAPI(
    title="🧠 CereBloom API",
    description="""
    ## CereBloom - Cabinet Médical avec IA de Segmentation

    Application spécialisée dans la segmentation de tumeurs cérébrales avec votre modèle U-Net Kaggle.

    ### 🎯 Fonctionnalités Principales:
    - **🔐 Authentification** : 3 rôles (Admin, Doctor, Secretary)
    - **🏥 Gestion Patients** : Dossiers médicaux complets
    - **🖼️ Images Médicales** : Support T1, T1CE, T2, FLAIR
    - **🧠 IA Segmentation** : Votre modèle U-Net pour tumeurs cérébrales
    - **💊 Traitements** : Prescriptions et suivi
    - **📅 Rendez-vous** : Planification et rappels
    - **📄 Rapports** : Génération automatique avec segmentations

    ### 🔗 Architecture:
    Basée sur le diagramme UML Relations et Flux de Données
    """,
    version="2.0.0",
    contact={
        "name": "CereBloom Team",
        "email": "support@cerebloom.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Configuration CORS - MISE À JOUR POUR CORRIGER LE PROBLÈME CORS
logger.info(f"CORS configure pour les origines: {settings.ALLOWED_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montage des fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Dépendance d'authentification
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Récupère l'utilisateur actuel à partir du token"""
    try:
        auth_service = AuthService()
        user = await auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide ou expiré"
            )
        return user
    except Exception as e:
        logger.error(f"Erreur d'authentification: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification échouée"
        )

# Routes principales
@app.get("/", tags=["🏠 Accueil"])
async def root():
    """Page d'accueil de l'API CereBloom"""
    return {
        "message": "🧠 Bienvenue sur CereBloom API",
        "description": "Cabinet médical avec IA de segmentation de tumeurs cérébrales",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "🔐 Authentification multi-rôles",
            "🏥 Gestion patients complète",
            "🖼️ Images médicales (T1, T1CE, T2, FLAIR)",
            "🧠 Segmentation IA avec votre modèle U-Net",
            "💊 Gestion des traitements",
            "📅 Système de rendez-vous",
            "📄 Rapports médicaux illustrés"
        ],
        "documentation": "/docs",
        "health_check": "/health"
    }

@app.get("/health", tags=["🏠 Accueil"])
async def health_check():
    """Vérification de l'état de santé de l'API"""
    try:
        # Test de connexion à la base de données
        db = await get_database()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "database": "connected",
            "services": {
                "auth": "operational",
                "ai_segmentation": "operational",
                "file_upload": "operational"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service indisponible"
        )

# Inclusion des routers
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["🔐 Authentification"])
app.include_router(users_router.router, prefix="/api/v1/users", tags=["👥 Utilisateurs"])
app.include_router(doctors_router.router, prefix="/api/v1/doctors", tags=["👨‍⚕️ Médecins"])
app.include_router(patients_router.router, prefix="/api/v1/patients", tags=["🏥 Patients"])
app.include_router(medical_images_router.router, prefix="/api/v1/images", tags=["🖼️ Images Médicales"])
app.include_router(ai_segmentation_router.router, prefix="/api/v1/segmentation", tags=["🧠 IA Segmentation"])  # ✅ Activé
app.include_router(treatments_router.router, prefix="/api/v1/treatments", tags=["💊 Traitements"])
app.include_router(appointments_router.router, prefix="/api/v1/appointments", tags=["📅 Rendez-vous"])
app.include_router(reports_router.router, prefix="/api/v1/reports", tags=["📄 Rapports"])
app.include_router(mlops_router.router, tags=["📊 MLOps"])  # ✅ AJOUTÉ : Router MLOps

# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire d'erreurs global"""
    logger.error(f"Erreur non gérée: {exc}")
    return {
        "error": "Erreur interne du serveur",
        "detail": str(exc) if settings.DEBUG else "Une erreur inattendue s'est produite",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("Lancement de CereBloom Backend...")
    uvicorn.run(
        "cerebloom_main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
