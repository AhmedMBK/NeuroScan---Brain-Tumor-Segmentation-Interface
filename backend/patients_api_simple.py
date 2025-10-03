#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API FastAPI simplifiée pour la gestion des patients (sans validation email).
"""

import os
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum

from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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

# Modèles Pydantic simplifiés
class EmergencyContact(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    relationship: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=10, max_length=20)

class Insurance(BaseModel):
    provider: str = Field(..., min_length=1, max_length=100)
    policy_number: str = Field(..., min_length=1, max_length=50)
    expiry_date: str = Field(..., description="Date au format YYYY-MM-DD")

class MedicalHistory(BaseModel):
    allergies: List[str] = Field(default_factory=list)
    chronic_conditions: List[str] = Field(default_factory=list)
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
    email: str = Field(..., min_length=5, max_length=100)  # Email simple sans validation
    address: str = Field(..., min_length=5, max_length=200)
    blood_type: BloodType
    height: int = Field(..., gt=0, le=300, description="Taille en cm")
    weight: float = Field(..., gt=0, le=500, description="Poids en kg")
    emergency_contact: EmergencyContact
    insurance: Insurance
    doctor: str = Field(..., min_length=1, max_length=100)
    medical_history: MedicalHistory
    notes: str = Field(default="", max_length=1000)

class Patient(PatientBase):
    id: str
    last_scan: Optional[str] = None
    last_visit: Optional[str] = None
    next_appointment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ScanBase(BaseModel):
    patient_id: str
    date: str = Field(..., description="Date au format YYYY-MM-DD")
    type: ScanType
    body_part: str = Field(..., min_length=1, max_length=100)
    result: ScanResult
    doctor: str = Field(..., min_length=1, max_length=100)
    facility: str = Field(..., min_length=1, max_length=100)
    status: ScanStatus = ScanStatus.PENDING

class Scan(ScanBase):
    id: str
    created_at: datetime
    updated_at: datetime

# Stockage en mémoire
patients_db: Dict[str, Patient] = {}
scans_db: Dict[str, Scan] = {}

# Fonctions utilitaires
def calculate_age(date_of_birth: str) -> int:
    """Calcule l'âge à partir de la date de naissance."""
    birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def generate_id() -> str:
    """Génère un ID unique."""
    return str(uuid.uuid4())

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API de Gestion des Patients (Simplifiée)",
    description="API simplifiée pour la gestion des patients et examens médicaux.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints de base
@app.get("/")
async def root():
    """Endpoint racine de l'API."""
    return {
        "message": "API de Gestion des Patients (Simplifiée)",
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
        "scans_count": len(scans_db)
    }

# Endpoints patients
@app.post("/patients", response_model=Patient, status_code=status.HTTP_201_CREATED)
async def create_patient(patient_data: PatientBase):
    """Crée un nouveau patient."""
    patient_id = generate_id()
    now = datetime.now()
    
    patient = Patient(
        id=patient_id,
        **patient_data.dict(),
        created_at=now,
        updated_at=now
    )
    
    patients_db[patient_id] = patient
    return patient

@app.get("/patients", response_model=List[Patient])
async def get_patients():
    """Récupère la liste des patients."""
    return list(patients_db.values())

@app.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    """Récupère un patient par son ID."""
    if patient_id not in patients_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    return patients_db[patient_id]

# Endpoints scans
@app.post("/scans", response_model=Scan, status_code=status.HTTP_201_CREATED)
async def create_scan(scan_data: ScanBase):
    """Crée un nouveau scan."""
    if scan_data.patient_id not in patients_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    scan_id = generate_id()
    now = datetime.now()
    
    scan = Scan(
        id=scan_id,
        **scan_data.dict(),
        created_at=now,
        updated_at=now
    )
    
    scans_db[scan_id] = scan
    return scan

@app.get("/scans", response_model=List[Scan])
async def get_scans():
    """Récupère la liste des scans."""
    return list(scans_db.values())

@app.get("/patients/{patient_id}/scans", response_model=List[Scan])
async def get_patient_scans(patient_id: str):
    """Récupère tous les scans d'un patient."""
    if patient_id not in patients_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    patient_scans = [s for s in scans_db.values() if s.patient_id == patient_id]
    return patient_scans

def create_sample_data():
    """Crée des données d'exemple."""
    now = datetime.now()
    
    # Patient d'exemple
    patient = Patient(
        id="patient-1",
        first_name="Jean",
        last_name="Dupont",
        date_of_birth="1980-05-15",
        gender=Gender.MALE,
        contact_number="+33123456789",
        email="jean.dupont@example.com",
        address="123 Rue de la Paix, Paris",
        blood_type=BloodType.A_POSITIVE,
        height=180,
        weight=75.5,
        emergency_contact=EmergencyContact(
            name="Marie Dupont",
            relationship="Épouse",
            phone="+33987654321"
        ),
        insurance=Insurance(
            provider="Sécurité Sociale",
            policy_number="1234567890",
            expiry_date="2024-12-31"
        ),
        doctor="Dr. Martin",
        medical_history=MedicalHistory(
            allergies=["Pénicilline"],
            chronic_conditions=["Hypertension"],
            family_history=["Diabète (Père)"]
        ),
        notes="Patient coopératif",
        created_at=now,
        updated_at=now
    )
    
    patients_db[patient.id] = patient
    
    # Scan d'exemple
    scan = Scan(
        id="scan-1",
        patient_id="patient-1",
        date="2023-10-12",
        type=ScanType.MRI,
        body_part="Cerveau",
        result=ScanResult(
            diagnosis="Glioblastome",
            tumor_type="Malin",
            tumor_size="3.2 cm",
            tumor_location="Lobe frontal droit",
            malignant=True,
            notes="Tumeur agressive avec œdème périphérique."
        ),
        doctor="Dr. Martin",
        facility="Hôpital Saint-Louis",
        status=ScanStatus.COMPLETED,
        created_at=now,
        updated_at=now
    )
    
    scans_db[scan.id] = scan
    
    print("✅ Données d'exemple créées!")
    print(f"   - {len(patients_db)} patient(s)")
    print(f"   - {len(scans_db)} scan(s)")

if __name__ == "__main__":
    # Créer les données d'exemple
    create_sample_data()
    
    print("\n🚀 Démarrage de l'API Simplifiée...")
    print("📖 Documentation: http://localhost:8001/docs")
    print("🔄 API: http://localhost:8001")
    
    # Démarrer le serveur
    uvicorn.run(
        "patients_api_simple:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
