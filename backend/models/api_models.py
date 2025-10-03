"""
🧠 CereBloom - Modèles Pydantic pour l'API
Modèles de validation et sérialisation des données
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date, time
from decimal import Decimal
from models.database_models import (
    UserRole, UserStatus, Gender, BloodType, ImageModality,
    SegmentationStatus, TumorType, TreatmentStatus, AppointmentStatus
)

# ===== MODÈLES DE BASE =====

class BaseResponse(BaseModel):
    """Modèle de base pour toutes les réponses"""
    success: bool = True
    message: str = "Opération réussie"
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    """Modèle pour les réponses d'erreur"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginationParams(BaseModel):
    """Paramètres de pagination"""
    page: int = Field(1, ge=1, description="Numéro de page")
    size: int = Field(10, ge=1, le=100, description="Taille de page")

class PaginatedResponse(BaseModel):
    """Réponse paginée"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

# ===== MODÈLES AUTHENTIFICATION =====

class LoginRequest(BaseModel):
    """Requête de connexion"""
    email: EmailStr = Field(..., description="Email de l'utilisateur")
    password: str = Field(..., min_length=6)

class LoginResponse(BaseModel):
    """Réponse de connexion"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"

class TokenRefreshRequest(BaseModel):
    """Requête de rafraîchissement de token"""
    refresh_token: str

class PasswordResetRequest(BaseModel):
    """Requête de réinitialisation de mot de passe"""
    email: EmailStr

class PasswordChangeRequest(BaseModel):
    """Requête de changement de mot de passe"""
    current_password: str
    new_password: str = Field(..., min_length=6)

# ===== MODÈLES UTILISATEURS =====

class UserCreate(BaseModel):
    """Création d'utilisateur"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    employee_id: Optional[str] = Field(None, max_length=50)
    assigned_doctor_id: Optional[str] = Field(None, description="ID du médecin assigné (pour les secrétaires uniquement)")

class UserUpdate(BaseModel):
    """Mise à jour d'utilisateur"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    status: Optional[UserStatus] = None
    profile_picture: Optional[str] = None
    assigned_doctor_id: Optional[str] = Field(None, description="ID du médecin assigné (pour les secrétaires uniquement)")

class UserResponse(BaseModel):
    """Réponse utilisateur"""
    id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    role: UserRole
    status: UserStatus
    profile_picture: Optional[str]
    employee_id: Optional[str]
    assigned_doctor_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserPermissionsResponse(BaseModel):
    """Réponse permissions utilisateur"""
    user_id: str
    can_view_patients: bool
    can_create_patients: bool
    can_edit_patients: bool
    can_delete_patients: bool
    can_view_segmentations: bool
    can_create_segmentations: bool
    can_validate_segmentations: bool
    can_manage_appointments: bool
    can_manage_users: bool
    can_view_reports: bool
    can_export_data: bool
    custom_permissions: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True

# ===== MODÈLES MÉDECINS =====

class DoctorCreate(BaseModel):
    """Création/Complétion de profil médecin"""
    bio: Optional[str] = Field(None, max_length=1000)
    office_location: Optional[str] = Field(None, max_length=200)

class DoctorUpdate(BaseModel):
    """Mise à jour de médecin"""
    bio: Optional[str] = Field(None, max_length=1000)
    office_location: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None

class DoctorResponse(BaseModel):
    """Réponse médecin"""
    id: str
    user_id: str
    bio: Optional[str]
    office_location: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== MODÈLES PATIENTS =====

class PatientCreate(BaseModel):
    """Création de patient"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: str = Field(..., description="Date au format YYYY-MM-DD")
    gender: Gender
    email: Optional[str] = Field(None, description="Email optionnel")
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    blood_type: Optional[BloodType] = None
    height: Optional[int] = Field(None, gt=0, le=300, description="Height in cm")
    weight: Optional[Decimal] = Field(None, gt=0, le=1000, description="Weight in kg")
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    assigned_doctor_id: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    insurance_number: Optional[str] = None
    notes: Optional[str] = None

class PatientUpdate(BaseModel):
    """Mise à jour de patient"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    blood_type: Optional[BloodType] = None
    height: Optional[int] = Field(None, gt=0, le=300)
    weight: Optional[Decimal] = Field(None, gt=0, le=1000)

    # Contact d'urgence - champs séparés
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None

    # Historique médical - champs séparés
    medical_history: Optional[str] = None
    allergies: Optional[str] = None

    assigned_doctor_id: Optional[str] = None
    notes: Optional[str] = None

class PatientResponse(BaseModel):
    """Réponse patient"""
    id: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    blood_type: Optional[BloodType]
    height: Optional[int]
    weight: Optional[Decimal]
    emergency_contact: Optional[Dict[str, Any]]
    assigned_doctor_id: Optional[str]
    assigned_doctor: Optional[Dict[str, Any]] = None  # Informations complètes du médecin
    medical_history: Optional[Dict[str, Any]]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== MODÈLES TRAITEMENTS =====

class TreatmentCreate(BaseModel):
    """Création de traitement"""
    patient_id: str
    prescribed_by_doctor_id: Optional[str] = None
    treatment_type: str = Field(..., min_length=1, max_length=100)
    medication_name: Optional[str] = Field(None, max_length=200)
    dosage: Optional[str] = Field(None, max_length=100)
    frequency: Optional[str] = Field(None, max_length=100)
    duration: Optional[str] = Field(None, max_length=100)
    start_date: date
    end_date: Optional[date] = None
    status: Optional[TreatmentStatus] = None
    notes: Optional[str] = None

class TreatmentResponse(BaseModel):
    """Réponse traitement"""
    id: str
    patient_id: str
    prescribed_by_doctor_id: str
    treatment_type: str
    medication_name: Optional[str]
    dosage: Optional[str]
    frequency: Optional[str]
    duration: Optional[str]
    start_date: date
    end_date: Optional[date]
    status: TreatmentStatus
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== MODÈLES RENDEZ-VOUS =====

class AppointmentCreate(BaseModel):
    """Création de rendez-vous"""
    patient_id: str
    doctor_id: str
    appointment_date: date
    appointment_time: time
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    appointment_type: Optional[str] = Field(None, max_length=100)

class AppointmentResponse(BaseModel):
    """Réponse rendez-vous"""
    id: str
    patient_id: str
    doctor_id: str
    scheduled_by_user_id: str
    appointment_date: date
    appointment_time: time
    status: AppointmentStatus
    notes: Optional[str]
    appointment_type: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



# ===== MODÈLES IMAGES MÉDICALES =====

class MedicalImageCreate(BaseModel):
    """Création d'image médicale"""
    patient_id: str
    modality: ImageModality
    file_path: str = Field(..., max_length=500)
    file_name: str = Field(..., max_length=255)
    file_size: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    acquisition_date: Optional[date] = None
    body_part: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    is_processed: Optional[bool] = False
    dicom_metadata: Optional[Dict[str, Any]] = None

class MedicalImageResponse(BaseModel):
    """Réponse image médicale"""
    id: str
    patient_id: str
    uploaded_by_user_id: str
    modality: ImageModality
    file_path: str
    file_name: str
    file_size: Optional[int]
    image_metadata: Optional[Dict[str, Any]]
    acquisition_date: Optional[date]
    body_part: Optional[str]
    notes: Optional[str]
    is_processed: bool
    dicom_metadata: Optional[Dict[str, Any]]
    uploaded_at: datetime

    class Config:
        from_attributes = True

# ===== MODÈLES RAPPORTS =====

class SegmentationReportCreate(BaseModel):
    """Création de rapport de segmentation"""
    segmentation_id: str
    doctor_id: Optional[str] = None
    report_content: str
    findings: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    image_attachments: Optional[Dict[str, Any]] = None
    template_used: Optional[str] = None
    quantitative_metrics: Optional[Dict[str, Any]] = None
    is_final: Optional[bool] = False

class SegmentationReportResponse(BaseModel):
    """Réponse rapport de segmentation"""
    id: str
    segmentation_id: str
    doctor_id: str
    report_content: str
    findings: Optional[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]]
    image_attachments: Optional[Dict[str, Any]]
    template_used: Optional[str]
    quantitative_metrics: Optional[Dict[str, Any]]
    is_final: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



class ImageSeriesCreate(BaseModel):
    """Création de série d'images"""
    patient_id: str
    series_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    image_ids: List[str]
    acquisition_date: date
    technical_parameters: Optional[Dict[str, Any]] = None

class ImageSeriesResponse(BaseModel):
    """Réponse série d'images"""
    id: str
    patient_id: str
    series_name: str
    description: Optional[str]
    image_ids: List[str]
    acquisition_date: date
    technical_parameters: Optional[Dict[str, Any]]
    study_instance_uid: Optional[str]
    series_instance_uid: Optional[str]
    slice_count: int
    created_at: datetime

    class Config:
        from_attributes = True

# ===== MODÈLES IA SEGMENTATION =====

class AISegmentationCreate(BaseModel):
    """Création de segmentation IA"""
    patient_id: str
    doctor_id: Optional[str] = None
    image_series_id: str
    input_parameters: Optional[Dict[str, Any]] = None

class AISegmentationResponse(BaseModel):
    """Réponse segmentation IA"""
    id: str
    patient_id: str
    doctor_id: Optional[str]
    image_series_id: str
    status: SegmentationStatus
    input_parameters: Optional[Dict[str, Any]]
    segmentation_results: Optional[Dict[str, Any]]
    volume_analysis: Optional[Dict[str, Any]]
    tumor_classification: Optional[Dict[str, Any]]
    confidence_score: Optional[Decimal]
    processing_time: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    validated_at: Optional[datetime]

    class Config:
        from_attributes = True

class TumorSegmentResponse(BaseModel):
    """Réponse segment tumoral"""
    id: str
    segmentation_id: str
    segment_type: TumorType
    volume_cm3: Decimal
    percentage: Decimal
    coordinates: Optional[Dict[str, Any]]
    contour_data: Optional[Dict[str, Any]]
    color_code: Optional[str]
    description: Optional[str]
    confidence_score: Optional[Decimal]
    statistical_features: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True

# Forward references
UserResponse.model_rebuild()
LoginResponse.model_rebuild()
