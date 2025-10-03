"""
🧠 CereBloom - Configuration et Settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Configuration de l'application CereBloom"""

    # 🔧 Configuration de base
    APP_NAME: str = "CereBloom"
    VERSION: str = "2.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 🔐 Sécurité
    SECRET_KEY: str = "cerebloom-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 heures
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 🗄️ Base de données
    DATABASE_URL: str = "postgresql+asyncpg://cerebloom_user:cerebloom_password@localhost:5432/cerebloom_db"
    DATABASE_ECHO: bool = False

    # 🐘 Configuration PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "cerebloom_db"
    POSTGRES_USER: str = "cerebloom_user"
    POSTGRES_PASSWORD: str = "cerebloom_password"

    # 🌐 CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080"
        # Pas de wildcard "*" car incompatible avec credentials: 'include'
    ]

    # 📁 Chemins de fichiers
    UPLOAD_DIR: str = "uploads"
    MEDICAL_IMAGES_DIR: str = "uploads/medical_images"
    SEGMENTATION_RESULTS_DIR: str = "uploads/segmentation_results"
    REPORTS_DIR: str = "uploads/reports"
    TEMP_DIR: str = "temp"

    # 📏 Limites de fichiers
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".nii", ".nii.gz", ".dcm", ".png", ".jpg", ".jpeg"]

    # 🧠 Configuration IA
    AI_MODEL_PATH: str = "models/my_model.h5"
    AI_MODEL_VERSION: str = "v2.1"
    AI_CONFIDENCE_THRESHOLD: float = 0.7
    AI_PROCESSING_TIMEOUT: int = 300  # 5 minutes

    # 📧 Configuration Email (pour les rappels)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True

    # 📱 Configuration SMS (pour les rappels)
    SMS_API_KEY: Optional[str] = None
    SMS_API_URL: Optional[str] = None

    # 🔍 Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/cerebloom.log"

    # 🎯 Configuration métier
    DEFAULT_CONSULTATION_DURATION: int = 30  # minutes
    MAX_APPOINTMENTS_PER_DAY: int = 20
    APPOINTMENT_REMINDER_HOURS: List[int] = [24, 2]  # Rappels à 24h et 2h avant

    # 🏥 Configuration cabinet
    CABINET_NAME: str = "CereBloom Medical Center"
    CABINET_ADDRESS: str = "123 Medical Street, Health City"
    CABINET_PHONE: str = "+1-234-567-8900"
    CABINET_EMAIL: str = "contact@cerebloom.com"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Instance globale des settings
settings = Settings()

# Création des dossiers nécessaires
def create_directories():
    """Crée les dossiers nécessaires pour l'application"""
    directories = [
        settings.UPLOAD_DIR,
        settings.MEDICAL_IMAGES_DIR,
        settings.SEGMENTATION_RESULTS_DIR,
        settings.REPORTS_DIR,
        settings.TEMP_DIR,
        "logs",
        "static"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Validation de la configuration
def validate_settings():
    """Valide la configuration de l'application"""
    errors = []

    # Vérification du modèle IA
    if not os.path.exists(settings.AI_MODEL_PATH):
        errors.append(f"Modèle IA non trouvé: {settings.AI_MODEL_PATH}")

    # Vérification de la clé secrète en production
    if not settings.DEBUG and settings.SECRET_KEY == "cerebloom-secret-key-change-in-production":
        errors.append("SECRET_KEY doit être changée en production")

    # Vérification des dossiers
    try:
        create_directories()
    except Exception as e:
        errors.append(f"Impossible de créer les dossiers: {e}")

    if errors:
        raise ValueError(f"Erreurs de configuration: {'; '.join(errors)}")

    return True

# Types d'utilisateurs et leurs permissions par défaut
USER_ROLE_PERMISSIONS = {
    "ADMIN": {
        "can_view_patients": True,
        "can_create_patients": True,
        "can_edit_patients": True,
        "can_delete_patients": True,
        "can_view_segmentations": True,
        "can_create_segmentations": True,
        "can_validate_segmentations": True,
        "can_manage_appointments": True,
        "can_manage_users": True,
        "can_view_reports": True,
        "can_export_data": True,
    },
    "DOCTOR": {
        "can_view_patients": True,
        "can_create_patients": True,
        "can_edit_patients": True,
        "can_delete_patients": False,
        "can_view_segmentations": True,
        "can_create_segmentations": True,
        "can_validate_segmentations": True,
        "can_manage_appointments": True,
        "can_manage_users": False,
        "can_view_reports": True,
        "can_export_data": True,
    },
    "SECRETARY": {
        "can_view_patients": True,
        "can_create_patients": True,
        "can_edit_patients": True,
        "can_delete_patients": False,
        "can_view_segmentations": True,
        "can_create_segmentations": False,
        "can_validate_segmentations": False,
        "can_manage_appointments": True,
        "can_manage_users": False,
        "can_view_reports": True,
        "can_export_data": False,
    }
}

# Configuration des couleurs pour les segments de tumeur
TUMOR_SEGMENT_COLORS = {
    "NECROTIC_CORE": "#FF0000",      # Rouge
    "PERITUMORAL_EDEMA": "#00FF00",  # Vert
    "ENHANCING_TUMOR": "#0000FF",    # Bleu
    "WHOLE_TUMOR": "#FFFF00"         # Jaune
}

# Configuration des types d'images médicales
IMAGE_MODALITY_CONFIG = {
    "T1": {
        "description": "T1-weighted MRI",
        "color": "#FF6B6B",
        "order": 1
    },
    "T1CE": {
        "description": "T1-weighted contrast-enhanced MRI",
        "color": "#4ECDC4",
        "order": 2
    },
    "T2": {
        "description": "T2-weighted MRI",
        "color": "#45B7D1",
        "order": 3
    },
    "FLAIR": {
        "description": "Fluid Attenuated Inversion Recovery",
        "color": "#FFA07A",
        "order": 4
    }
}

# Messages d'erreur standardisés
ERROR_MESSAGES = {
    "USER_NOT_FOUND": "Utilisateur non trouvé",
    "INVALID_CREDENTIALS": "Identifiants invalides",
    "ACCESS_DENIED": "Accès refusé",
    "PATIENT_NOT_FOUND": "Patient non trouvé",
    "IMAGE_NOT_FOUND": "Image non trouvée",
    "SEGMENTATION_FAILED": "Échec de la segmentation",
    "INVALID_FILE_FORMAT": "Format de fichier invalide",
    "FILE_TOO_LARGE": "Fichier trop volumineux",
    "APPOINTMENT_CONFLICT": "Conflit de rendez-vous",
    "TREATMENT_NOT_FOUND": "Traitement non trouvé"
}

# Validation au démarrage
if __name__ == "__main__":
    validate_settings()
    print("✅ Configuration validée avec succès")
