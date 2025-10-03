#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API FastAPI pour la gestion des patients et examens médicaux.
Cette API permet de gérer les patients, leurs examens, traitements et rendez-vous.
"""

import os
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum

from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, validator
import uvicorn

# Énumérations pour les types de données
class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class BloodType(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class ScanType(str, Enum):
    MRI = "MRI"
    CT = "CT"
    PET = "PET"
    XRAY = "X-Ray"

class ScanStatus(str, Enum):
    COMPLETED = "Completed"
    PENDING = "Pending"
    PROCESSING = "Processing"
    FAILED = "Failed"

class TreatmentType(str, Enum):
    MEDICATION = "Medication"
    SURGERY = "Surgery"
    RADIATION = "Radiation"
    CHEMOTHERAPY = "Chemotherapy"
    PHYSICAL_THERAPY = "Physical Therapy"
    OTHER = "Other"

class TreatmentStatus(str, Enum):
    ACTIVE = "Active"
    COMPLETED = "Completed"
    SCHEDULED = "Scheduled"
    CANCELLED = "Cancelled"

class Effectiveness(str, Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    MODERATE = "Moderate"
    POOR = "Poor"
    UNKNOWN = "Unknown"

class AppointmentStatus(str, Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    NO_SHOW = "No-Show"

# Modèles Pydantic pour les données imbriquées
class EmergencyContact(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    relationship: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=10, max_length=20)

class Insurance(BaseModel):
    provider: str = Field(..., min_length=1, max_length=100)
    policy_number: str = Field(..., min_length=1, max_length=50)
    expiry_date: str = Field(..., description="Date au format YYYY-MM-DD")

class PastSurgery(BaseModel):
    procedure: str = Field(..., min_length=1, max_length=200)
    date: str = Field(..., description="Date au format YYYY-MM-DD")
    notes: str = Field(default="", max_length=500)

class MedicalHistory(BaseModel):
    allergies: List[str] = Field(default_factory=list)
    chronic_conditions: List[str] = Field(default_factory=list)
    past_surgeries: List[PastSurgery] = Field(default_factory=list)
    family_history: List[str] = Field(default_factory=list)

class ScanResult(BaseModel):
    diagnosis: str = Field(..., min_length=1, max_length=200)
    tumor_type: Optional[str] = Field(None, max_length=100)
    tumor_size: Optional[str] = Field(None, max_length=50)
    tumor_location: Optional[str] = Field(None, max_length=100)
    malignant: Optional[bool] = None
    notes: str = Field(default="", max_length=1000)

# Modèles principaux
class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: str = Field(..., description="Date au format YYYY-MM-DD")
    gender: Gender
    contact_number: str = Field(..., min_length=10, max_length=20)
    email: EmailStr
    address: str = Field(..., min_length=5, max_length=200)
    blood_type: BloodType
    height: int = Field(..., gt=0, le=300, description="Taille en cm")
    weight: float = Field(..., gt=0, le=500, description="Poids en kg")
    emergency_contact: EmergencyContact
    insurance: Insurance
    doctor: str = Field(..., min_length=1, max_length=100)
    medical_history: MedicalHistory
    notes: str = Field(default="", max_length=1000)

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    date_of_birth: Optional[str] = None
    gender: Optional[Gender] = None
    contact_number: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, min_length=5, max_length=200)
    blood_type: Optional[BloodType] = None
    height: Optional[int] = Field(None, gt=0, le=300)
    weight: Optional[float] = Field(None, gt=0, le=500)
    emergency_contact: Optional[EmergencyContact] = None
    insurance: Optional[Insurance] = None
    doctor: Optional[str] = Field(None, min_length=1, max_length=100)
    medical_history: Optional[MedicalHistory] = None
    notes: Optional[str] = Field(None, max_length=1000)

class Patient(PatientBase):
    id: str
    last_scan: Optional[str] = None
    last_visit: Optional[str] = None
    next_appointment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ScanBase(BaseModel):
    patient_id: str
    date: str = Field(..., description="Date au format YYYY-MM-DD")
    type: ScanType
    body_part: str = Field(..., min_length=1, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    result: ScanResult
    doctor: str = Field(..., min_length=1, max_length=100)
    facility: str = Field(..., min_length=1, max_length=100)
    status: ScanStatus = ScanStatus.PENDING

class ScanCreate(ScanBase):
    pass

class ScanUpdate(BaseModel):
    date: Optional[str] = None
    type: Optional[ScanType] = None
    body_part: Optional[str] = Field(None, min_length=1, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    result: Optional[ScanResult] = None
    doctor: Optional[str] = Field(None, min_length=1, max_length=100)
    facility: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[ScanStatus] = None

class Scan(ScanBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Modèles pour les traitements
class TreatmentBase(BaseModel):
    patient_id: str
    type: TreatmentType
    name: str = Field(..., min_length=1, max_length=200)
    start_date: str = Field(..., description="Date au format YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="Date au format YYYY-MM-DD")
    frequency: Optional[str] = Field(None, max_length=100)
    dosage: Optional[str] = Field(None, max_length=100)
    doctor: str = Field(..., min_length=1, max_length=100)
    notes: str = Field(default="", max_length=1000)
    status: TreatmentStatus = TreatmentStatus.SCHEDULED
    side_effects: List[str] = Field(default_factory=list)
    effectiveness: Effectiveness = Effectiveness.UNKNOWN

class TreatmentCreate(TreatmentBase):
    pass

class TreatmentUpdate(BaseModel):
    type: Optional[TreatmentType] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    frequency: Optional[str] = Field(None, max_length=100)
    dosage: Optional[str] = Field(None, max_length=100)
    doctor: Optional[str] = Field(None, min_length=1, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[TreatmentStatus] = None
    side_effects: Optional[List[str]] = None
    effectiveness: Optional[Effectiveness] = None

class Treatment(TreatmentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Modèles pour les rendez-vous
class AppointmentBase(BaseModel):
    patient_id: str
    date: str = Field(..., description="Date au format YYYY-MM-DD")
    time: str = Field(..., description="Heure au format HH:MM AM/PM")
    doctor: str = Field(..., min_length=1, max_length=100)
    purpose: str = Field(..., min_length=1, max_length=200)
    notes: str = Field(default="", max_length=1000)
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    follow_up: bool = False

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    doctor: Optional[str] = Field(None, min_length=1, max_length=100)
    purpose: Optional[str] = Field(None, min_length=1, max_length=200)
    notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[AppointmentStatus] = None
    follow_up: Optional[bool] = None

class Appointment(AppointmentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Modèles de réponse
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

class PatientResponse(BaseModel):
    patient: Patient
    scans_count: int
    treatments_count: int
    appointments_count: int

class PatientSummary(BaseModel):
    id: str
    first_name: str
    last_name: str
    age: int
    gender: Gender
    last_scan: Optional[str] = None
    last_visit: Optional[str] = None
    next_appointment: Optional[str] = None
    doctor: str

# Stockage en mémoire (à remplacer par une base de données en production)
patients_db: Dict[str, Patient] = {}
scans_db: Dict[str, Scan] = {}
treatments_db: Dict[str, Treatment] = {}
appointments_db: Dict[str, Appointment] = {}

# Fonctions utilitaires
def calculate_age(date_of_birth: str) -> int:
    """Calcule l'âge à partir de la date de naissance."""
    birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def generate_id() -> str:
    """Génère un ID unique."""
    return str(uuid.uuid4())

def get_patient_last_scan(patient_id: str) -> Optional[str]:
    """Récupère la date du dernier scan d'un patient."""
    patient_scans = [scan for scan in scans_db.values() if scan.patient_id == patient_id]
    if not patient_scans:
        return None
    latest_scan = max(patient_scans, key=lambda x: x.date)
    return latest_scan.date

def get_patient_next_appointment(patient_id: str) -> Optional[str]:
    """Récupère la date du prochain rendez-vous d'un patient."""
    patient_appointments = [
        apt for apt in appointments_db.values()
        if apt.patient_id == patient_id and apt.status == AppointmentStatus.SCHEDULED
    ]
    if not patient_appointments:
        return None
    next_apt = min(patient_appointments, key=lambda x: x.date)
    return next_apt.date

def update_patient_metadata(patient_id: str):
    """Met à jour les métadonnées d'un patient (dernier scan, prochain RDV)."""
    if patient_id in patients_db:
        patient = patients_db[patient_id]
        patient.last_scan = get_patient_last_scan(patient_id)
        patient.next_appointment = get_patient_next_appointment(patient_id)
        patient.updated_at = datetime.now()

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API de Gestion des Patients",
    description="API complète pour la gestion des patients, examens, traitements et rendez-vous médicaux.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints racine
@app.get("/")
async def root():
    """Endpoint racine de l'API."""
    return {
        "message": "API de Gestion des Patients",
        "status": "active",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état de l'API."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "patients_count": len(patients_db),
        "scans_count": len(scans_db),
        "treatments_count": len(treatments_db),
        "appointments_count": len(appointments_db)
    }
