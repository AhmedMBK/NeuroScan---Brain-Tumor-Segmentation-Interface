"""
🧠 CereBloom - Modèles de Base de Données
Basés sur le diagramme UML Relations et Flux de Données
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Time, Text, JSON, DECIMAL, Enum, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
import enum
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any

# ===== ÉNUMÉRATIONS =====

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    SECRETARY = "SECRETARY"

class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"

class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class BloodType(str, enum.Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class ImageModality(str, enum.Enum):
    T1 = "T1"
    T1CE = "T1CE"
    T2 = "T2"
    FLAIR = "FLAIR"
    DWI = "DWI"
    DTI = "DTI"

class SegmentationStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    VALIDATED = "VALIDATED"
    PENDING_REVIEW = "PENDING_REVIEW"

class TumorType(str, enum.Enum):
    NECROTIC_CORE = "NECROTIC_CORE"
    PERITUMORAL_EDEMA = "PERITUMORAL_EDEMA"
    ENHANCING_TUMOR = "ENHANCING_TUMOR"
    WHOLE_TUMOR = "WHOLE_TUMOR"

class TreatmentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    SUSPENDED = "SUSPENDED"
    MODIFIED = "MODIFIED"

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"



# ===== MODÈLES SYSTÈME UTILISATEURS =====

class User(Base):
    """🔐 Table centrale des utilisateurs"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    role = Column(Enum(UserRole), nullable=False, index=True)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_VERIFICATION, index=True)
    profile_picture = Column(String(500))
    employee_id = Column(String(50), unique=True, index=True)
    assigned_doctor_id = Column(String(36), ForeignKey("doctors.id"), nullable=True, index=True, comment="Pour les secrétaires: médecin assigné")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(String(36), ForeignKey("users.id"))

    # Relations
    credentials = relationship("UserCredentials", back_populates="user", uselist=False, cascade="all, delete-orphan")
    permissions = relationship("UserPermissions", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    # ✅ CORRIGÉ : Spécification explicite des foreign_keys pour éviter l'ambiguïté
    doctor_profile = relationship(
        "Doctor",
        foreign_keys="Doctor.user_id",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    assigned_doctor = relationship(
        "Doctor",
        foreign_keys=[assigned_doctor_id],
        post_update=True
    )

    # Relations de création
    created_patients = relationship("Patient", foreign_keys="Patient.created_by_user_id", back_populates="created_by_user")
    uploaded_images = relationship("MedicalImage", back_populates="uploaded_by_user")
    scheduled_appointments = relationship("Appointment", foreign_keys="Appointment.scheduled_by_user_id", back_populates="scheduled_by_user")
    created_templates = relationship("ReportTemplate", back_populates="created_by_user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

# ===== MODÈLES AUTHENTIFICATION AVANCÉE =====

class UserCredentials(Base):
    """🔐 Gestion avancée des identifiants utilisateur"""
    __tablename__ = "user_credentials"

    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    last_login = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    locked_until = Column(DateTime)
    reset_token = Column(String(255))
    token_expires_at = Column(DateTime)

    # Relations
    user = relationship("User", back_populates="credentials")

    def __repr__(self):
        return f"<UserCredentials(user_id={self.user_id}, username={self.username})>"

class UserPermissions(Base):
    """🛡️ Système de permissions granulaires"""
    __tablename__ = "user_permissions"

    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    can_view_patients = Column(Boolean, default=False)
    can_create_patients = Column(Boolean, default=False)
    can_edit_patients = Column(Boolean, default=False)
    can_delete_patients = Column(Boolean, default=False)
    can_view_segmentations = Column(Boolean, default=False)
    can_create_segmentations = Column(Boolean, default=False)
    can_validate_segmentations = Column(Boolean, default=False)
    can_manage_appointments = Column(Boolean, default=False)
    can_manage_users = Column(Boolean, default=False)
    can_view_reports = Column(Boolean, default=False)
    can_export_data = Column(Boolean, default=False)
    custom_permissions = Column(JSON)

    # Relations
    user = relationship("User", back_populates="permissions")

    def __repr__(self):
        return f"<UserPermissions(user_id={self.user_id})>"

class UserSession(Base):
    """🔄 Gestion des sessions utilisateur"""
    __tablename__ = "user_sessions"

    session_id = Column(String(255), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime, default=func.now())

    # Relations
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(session_id={self.session_id}, user_id={self.user_id})>"



# ===== MODÈLES SYSTÈME MÉDECINS =====

class Doctor(Base):
    """👨‍⚕️ Profils des médecins - Conforme au diagramme de classes"""
    __tablename__ = "doctors"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    bio = Column(Text)
    office_location = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    # ✅ CORRIGÉ : Spécification explicite des foreign_keys pour éviter l'ambiguïté
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="doctor_profile"
    )
    patients = relationship("Patient", back_populates="assigned_doctor")
    medical_records = relationship("MedicalRecord", back_populates="doctor")
    segmentations = relationship("AISegmentation", back_populates="doctor")
    treatments = relationship("Treatment", back_populates="prescribed_by_doctor")
    appointments = relationship("Appointment", foreign_keys="Appointment.doctor_id", back_populates="doctor")
    segmentation_reports = relationship("SegmentationReport", back_populates="doctor")

    def __repr__(self):
        return f"<Doctor(id={self.id}, user_id={self.user_id})>"

# ===== MODÈLES SYSTÈME PATIENTS =====

class Patient(Base):
    """🏥 Dossiers des patients"""
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(Text)
    blood_type = Column(Enum(BloodType))
    height = Column(Integer, comment="Height in cm")
    weight = Column(DECIMAL(5, 2), comment="Weight in kg")
    emergency_contact = Column(JSON)
    assigned_doctor_id = Column(String(36), ForeignKey("doctors.id"), index=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    medical_history = Column(JSON)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    assigned_doctor = relationship("Doctor", back_populates="patients")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id], back_populates="created_patients")
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    medical_images = relationship("MedicalImage", back_populates="patient", cascade="all, delete-orphan")
    image_series = relationship("ImageSeries", back_populates="patient", cascade="all, delete-orphan")
    segmentations = relationship("AISegmentation", back_populates="patient", cascade="all, delete-orphan")
    treatments = relationship("Treatment", back_populates="patient", cascade="all, delete-orphan")
    appointments = relationship("Appointment", foreign_keys="Appointment.patient_id", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient(id={self.id}, name={self.first_name} {self.last_name})>"

class MedicalRecord(Base):
    """📋 Dossiers médicaux et consultations"""
    __tablename__ = "medical_records"

    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(String(36), ForeignKey("doctors.id"), nullable=False, index=True)
    consultation_date = Column(Date, nullable=False)
    chief_complaint = Column(Text)
    symptoms = Column(Text)
    physical_examination = Column(Text)
    diagnosis = Column(Text)
    notes = Column(Text)
    vital_signs = Column(JSON)
    is_final = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")

    def __repr__(self):
        return f"<MedicalRecord(id={self.id}, patient_id={self.patient_id}, date={self.consultation_date})>"

# ===== MODÈLES SYSTÈME IMAGES MÉDICALES =====

class MedicalImage(Base):
    """🖼️ Images médicales individuelles"""
    __tablename__ = "medical_images"

    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    uploaded_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    modality = Column(Enum(ImageModality), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False, comment="File size in bytes")
    image_metadata = Column(JSON)
    acquisition_date = Column(Date)
    body_part = Column(String(100))
    notes = Column(Text)
    is_processed = Column(Boolean, default=False)
    dicom_metadata = Column(JSON)
    uploaded_at = Column(DateTime, default=func.now())

    # Relations
    patient = relationship("Patient", back_populates="medical_images")
    uploaded_by_user = relationship("User", back_populates="uploaded_images")

    def __repr__(self):
        return f"<MedicalImage(id={self.id}, modality={self.modality}, patient_id={self.patient_id})>"

class ImageSeries(Base):
    """📁 Séries d'images groupées"""
    __tablename__ = "image_series"

    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    series_name = Column(String(200), nullable=False)
    description = Column(Text)
    image_ids = Column(JSON, comment="Array of image IDs")
    acquisition_date = Column(Date, nullable=False)
    technical_parameters = Column(JSON)
    study_instance_uid = Column(String(100))
    series_instance_uid = Column(String(100))
    slice_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    # Relations
    patient = relationship("Patient", back_populates="image_series")
    segmentations = relationship("AISegmentation", back_populates="image_series")

    def __repr__(self):
        return f"<ImageSeries(id={self.id}, name={self.series_name}, patient_id={self.patient_id})>"

# ===== CŒUR IA - SEGMENTATION (VOTRE MODÈLE U-NET) =====

class AISegmentation(Base):
    """🧠 Segmentations IA - Cœur de l'application"""
    __tablename__ = "ai_segmentations"

    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(String(36), ForeignKey("doctors.id"), nullable=True, index=True)
    image_series_id = Column(String(36), ForeignKey("image_series.id"), nullable=False)
    status = Column(Enum(SegmentationStatus), default=SegmentationStatus.PROCESSING, index=True)
    input_parameters = Column(JSON)
    segmentation_results = Column(JSON)
    volume_analysis = Column(JSON)
    tumor_classification = Column(JSON)
    confidence_score = Column(DECIMAL(5, 4), comment="Confidence score 0.0000 to 1.0000")
    processing_time = Column(String(50), comment="Processing time like '2.5 minutes'")
    preprocessing_params = Column(JSON)
    postprocessing_params = Column(JSON)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    validated_at = Column(DateTime)

    # Relations
    patient = relationship("Patient", back_populates="segmentations")
    doctor = relationship("Doctor", back_populates="segmentations")
    image_series = relationship("ImageSeries", back_populates="segmentations")
    tumor_segments = relationship("TumorSegment", back_populates="segmentation", cascade="all, delete-orphan")
    volumetric_analysis = relationship("VolumetricAnalysis", back_populates="segmentation", uselist=False, cascade="all, delete-orphan")
    segmentation_reports = relationship("SegmentationReport", back_populates="segmentation", cascade="all, delete-orphan")
    current_comparisons = relationship("SegmentationComparison", foreign_keys="SegmentationComparison.current_segmentation_id", back_populates="current_segmentation")
    previous_comparisons = relationship("SegmentationComparison", foreign_keys="SegmentationComparison.previous_segmentation_id", back_populates="previous_segmentation")

    def __repr__(self):
        return f"<AISegmentation(id={self.id}, status={self.status}, patient_id={self.patient_id})>"

class TumorSegment(Base):
    """🎯 Segments tumoraux détaillés"""
    __tablename__ = "tumor_segments"

    id = Column(String(36), primary_key=True)
    segmentation_id = Column(String(36), ForeignKey("ai_segmentations.id"), nullable=False, index=True)
    segment_type = Column(Enum(TumorType), nullable=False, index=True)
    volume_cm3 = Column(DECIMAL(10, 4), nullable=False, comment="Volume in cm³")
    percentage = Column(DECIMAL(5, 2), nullable=False, comment="Percentage of total volume")
    coordinates = Column(JSON, comment="3D coordinates")
    contour_data = Column(JSON, comment="Contour data")
    color_code = Column(String(7), comment="Hex color code like #FF0000")
    description = Column(Text)
    confidence_score = Column(DECIMAL(5, 4))
    statistical_features = Column(JSON)
    created_at = Column(DateTime, default=func.now())

    # Relations
    segmentation = relationship("AISegmentation", back_populates="tumor_segments")

    def __repr__(self):
        return f"<TumorSegment(id={self.id}, type={self.segment_type}, volume={self.volume_cm3})>"

class VolumetricAnalysis(Base):
    """📊 Analyse volumétrique complète"""
    __tablename__ = "volumetric_analysis"

    id = Column(String(36), primary_key=True)
    segmentation_id = Column(String(36), ForeignKey("ai_segmentations.id"), unique=True, nullable=False)
    total_tumor_volume = Column(DECIMAL(10, 4), nullable=False, comment="Total volume in cm³")
    necrotic_core_volume = Column(DECIMAL(10, 4), default=0.0000)
    peritumoral_edema_volume = Column(DECIMAL(10, 4), default=0.0000)
    enhancing_tumor_volume = Column(DECIMAL(10, 4), default=0.0000)
    evolution_data = Column(JSON, comment="Temporal evolution data")
    comparison_previous = Column(JSON, comment="Comparison with previous exam")
    tumor_burden_index = Column(DECIMAL(8, 4), comment="Tumor burden index")
    growth_rate_analysis = Column(JSON)
    analysis_date = Column(DateTime, default=func.now())

    # Relations
    segmentation = relationship("AISegmentation", back_populates="volumetric_analysis")

    def __repr__(self):
        return f"<VolumetricAnalysis(id={self.id}, total_volume={self.total_tumor_volume})>"

class SegmentationComparison(Base):
    """🔄 Comparaisons de segmentations temporelles"""
    __tablename__ = "segmentation_comparisons"

    id = Column(String(36), primary_key=True)
    current_segmentation_id = Column(String(36), ForeignKey("ai_segmentations.id"), nullable=False)
    previous_segmentation_id = Column(String(36), ForeignKey("ai_segmentations.id"), nullable=False)
    volume_changes = Column(JSON, comment="Volume changes per segment")
    morphological_changes = Column(JSON, comment="Morphological changes")
    change_percentage = Column(DECIMAL(6, 2), comment="Global change percentage")
    interpretation = Column(Text, comment="Clinical interpretation")
    statistical_analysis = Column(JSON)
    comparison_date = Column(DateTime, default=func.now())

    # Relations
    current_segmentation = relationship("AISegmentation", foreign_keys=[current_segmentation_id], back_populates="current_comparisons")
    previous_segmentation = relationship("AISegmentation", foreign_keys=[previous_segmentation_id], back_populates="previous_comparisons")

    def __repr__(self):
        return f"<SegmentationComparison(id={self.id}, change={self.change_percentage}%)>"

# ===== MODÈLES SYSTÈME TRAITEMENTS =====

class Treatment(Base):
    """💊 Traitements et prescriptions"""
    __tablename__ = "treatments"

    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    prescribed_by_doctor_id = Column(String(36), ForeignKey("doctors.id"), nullable=False)
    treatment_type = Column(String(100), nullable=False, comment="Chimiothérapie, Radiothérapie, etc.")
    medication_name = Column(String(200))
    dosage = Column(String(100))
    frequency = Column(String(100), comment="2 fois par jour")
    duration = Column(String(100), comment="4 semaines")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    status = Column(Enum(TreatmentStatus), default=TreatmentStatus.ACTIVE, index=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    patient = relationship("Patient", back_populates="treatments")
    prescribed_by_doctor = relationship("Doctor", back_populates="treatments")

    def __repr__(self):
        return f"<Treatment(id={self.id}, type={self.treatment_type}, patient_id={self.patient_id})>"

# ===== MODÈLES SYSTÈME RENDEZ-VOUS =====

class Appointment(Base):
    """📅 Rendez-vous et consultations"""
    __tablename__ = "appointments"

    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(String(36), ForeignKey("doctors.id"), nullable=False, index=True)
    scheduled_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    appointment_date = Column(Date, nullable=False, index=True)
    appointment_time = Column(Time, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, index=True)
    notes = Column(Text)
    previous_appointment_id = Column(String(36), ForeignKey("appointments.id"))
    appointment_type = Column(String(100), comment="CONSULTATION, FOLLOW_UP, EMERGENCY")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    patient = relationship("Patient", foreign_keys=[patient_id], back_populates="appointments")
    doctor = relationship("Doctor", foreign_keys=[doctor_id], back_populates="appointments")
    scheduled_by_user = relationship("User", foreign_keys=[scheduled_by_user_id], back_populates="scheduled_appointments")

    def __repr__(self):
        return f"<Appointment(id={self.id}, date={self.appointment_date}, patient_id={self.patient_id})>"



# ===== MODÈLES SYSTÈME RAPPORTS =====

class ReportTemplate(Base):
    """📋 Templates de rapports personnalisables"""
    __tablename__ = "report_templates"

    id = Column(String(36), primary_key=True)
    template_name = Column(String(200), nullable=False)
    template_type = Column(String(100), nullable=False, comment="SEGMENTATION, CONSULTATION, etc.")
    content_template = Column(Text, nullable=False, comment="HTML/Markdown template")
    fields_mapping = Column(JSON, comment="Dynamic fields mapping")
    category = Column(String(100))
    default_values = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    created_by_user = relationship("User", back_populates="created_templates")
    segmentation_reports = relationship("SegmentationReport", back_populates="template")

    def __repr__(self):
        return f"<ReportTemplate(id={self.id}, name={self.template_name}, type={self.template_type})>"

class SegmentationReport(Base):
    """📊 Rapports de segmentation illustrés"""
    __tablename__ = "segmentation_reports"

    id = Column(String(36), primary_key=True)
    segmentation_id = Column(String(36), ForeignKey("ai_segmentations.id"), nullable=False, index=True)
    doctor_id = Column(String(36), ForeignKey("doctors.id"), nullable=False)
    report_content = Column(Text, nullable=False)
    findings = Column(JSON, comment="Clinical findings")
    recommendations = Column(JSON, comment="Clinical recommendations")
    image_attachments = Column(JSON, comment="Segmentation images")
    template_used = Column(String(36), ForeignKey("report_templates.id"))
    quantitative_metrics = Column(JSON, comment="Quantitative metrics")
    is_final = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    segmentation = relationship("AISegmentation", back_populates="segmentation_reports")
    doctor = relationship("Doctor", back_populates="segmentation_reports")
    template = relationship("ReportTemplate", back_populates="segmentation_reports")

    def __repr__(self):
        return f"<SegmentationReport(id={self.id}, segmentation_id={self.segmentation_id}, final={self.is_final})>"
