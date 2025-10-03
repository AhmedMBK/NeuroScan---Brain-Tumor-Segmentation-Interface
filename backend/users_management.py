#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestion complète des utilisateurs et médecins pour l'API CereBloom.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

from fastapi import FastAPI, HTTPException, Query, Depends, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import uvicorn

# Énumérations pour les utilisateurs
class UserRole(str, Enum):
    ADMIN = "Admin"
    DOCTOR = "Doctor"
    NURSE = "Nurse"
    TECHNICIAN = "Technician"
    RECEPTIONIST = "Receptionist"

class UserStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"
    PENDING_VERIFICATION = "Pending Verification"

class DoctorSpecialty(str, Enum):
    NEUROLOGY = "Neurology"
    ONCOLOGY = "Oncology"
    RADIOLOGY = "Radiology"
    NEUROSURGERY = "Neurosurgery"
    GENERAL_MEDICINE = "General Medicine"
    PSYCHIATRY = "Psychiatry"
    ANESTHESIOLOGY = "Anesthesiology"

class DoctorStatus(str, Enum):
    ACTIVE = "Active"
    ON_LEAVE = "On Leave"
    RETIRED = "Retired"
    SUSPENDED = "Suspended"

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

# Classes de données pour les utilisateurs
class UserCredentials(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password_hash: str
    salt: str
    last_login: Optional[datetime] = None
    failed_login_attempts: int = Field(default=0, ge=0)
    is_locked: bool = Field(default=False)
    locked_until: Optional[datetime] = None
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None

class UserPermissions(BaseModel):
    can_view_patients: bool = Field(default=False)
    can_create_patients: bool = Field(default=False)
    can_edit_patients: bool = Field(default=False)
    can_delete_patients: bool = Field(default=False)
    can_view_scans: bool = Field(default=False)
    can_create_scans: bool = Field(default=False)
    can_view_treatments: bool = Field(default=False)
    can_create_treatments: bool = Field(default=False)
    can_view_appointments: bool = Field(default=False)
    can_create_appointments: bool = Field(default=False)
    can_manage_users: bool = Field(default=False)
    can_view_reports: bool = Field(default=False)
    custom_permissions: List[str] = Field(default_factory=list)

# Classes de base pour les utilisateurs
class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    gender: Gender
    date_of_birth: str = Field(..., description="Date au format YYYY-MM-DD")
    address: str = Field(..., min_length=5, max_length=200)
    role: UserRole
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    is_verified: bool = Field(default=False)
    profile_picture: Optional[str] = Field(None, max_length=500)
    notes: str = Field(default="", max_length=1000)

class User(UserBase):
    id: str
    credentials: UserCredentials
    permissions: UserPermissions
    department: Optional[str] = Field(None, max_length=100)
    employee_id: Optional[str] = Field(None, max_length=50)
    created_at: datetime
    updated_at: datetime
    last_activity: Optional[datetime] = None
    created_by: str

    class Config:
        from_attributes = True

# Classes pour les médecins
class DoctorEducation(BaseModel):
    degree: str = Field(..., min_length=1, max_length=100)
    institution: str = Field(..., min_length=1, max_length=200)
    graduation_year: str = Field(..., min_length=4, max_length=4)
    country: str = Field(..., min_length=2, max_length=100)

class DoctorCertification(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    issuing_body: str = Field(..., min_length=1, max_length=200)
    issue_date: str = Field(..., description="Date au format YYYY-MM-DD")
    expiry_date: Optional[str] = Field(None, description="Date au format YYYY-MM-DD")
    certificate_number: str = Field(..., min_length=1, max_length=100)
    is_active: bool = Field(default=True)

class DoctorSchedule(BaseModel):
    day_of_week: str = Field(..., description="Lundi, Mardi, etc.")
    start_time: str = Field(..., description="HH:MM")
    end_time: str = Field(..., description="HH:MM")
    is_available: bool = Field(default=True)
    notes: Optional[str] = Field(None, max_length=200)

class DoctorBase(BaseModel):
    license_number: str = Field(..., min_length=1, max_length=50)
    specialty: DoctorSpecialty
    sub_specialties: List[DoctorSpecialty] = Field(default_factory=list)
    years_of_experience: int = Field(..., ge=0, le=70)
    education: List[DoctorEducation] = Field(default_factory=list)
    certifications: List[DoctorCertification] = Field(default_factory=list)
    languages_spoken: List[str] = Field(default_factory=list)
    consultation_fee: str = Field(..., description="Tarif de consultation")
    schedule: List[DoctorSchedule] = Field(default_factory=list)
    status: DoctorStatus = DoctorStatus.ACTIVE
    bio: Optional[str] = Field(None, max_length=2000)
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    total_reviews: int = Field(default=0, ge=0)

class Doctor(DoctorBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Classes pour les sessions
class UserSession(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool = Field(default=True)
    last_activity: Optional[datetime] = None

class RefreshToken(BaseModel):
    token_id: str
    user_id: str
    token_hash: str
    created_at: datetime
    expires_at: datetime
    is_revoked: bool = Field(default=False)
    revoked_by: Optional[str] = None
    revoked_at: Optional[datetime] = None

# Classes DTO
class UserCreate(UserBase):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = Field(None, min_length=5, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    gender: Optional[Gender] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = Field(None, min_length=5, max_length=200)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    department: Optional[str] = Field(None, max_length=100)
    employee_id: Optional[str] = Field(None, max_length=50)
    profile_picture: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)

class DoctorCreate(DoctorBase):
    user_id: str

class DoctorUpdate(BaseModel):
    license_number: Optional[str] = Field(None, min_length=1, max_length=50)
    specialty: Optional[DoctorSpecialty] = None
    sub_specialties: Optional[List[DoctorSpecialty]] = None
    years_of_experience: Optional[int] = Field(None, ge=0, le=70)
    education: Optional[List[DoctorEducation]] = None
    certifications: Optional[List[DoctorCertification]] = None
    languages_spoken: Optional[List[str]] = None
    consultation_fee: Optional[str] = None
    schedule: Optional[List[DoctorSchedule]] = None
    status: Optional[DoctorStatus] = None
    bio: Optional[str] = Field(None, max_length=2000)

# Classes de réponse
class UserResponse(BaseModel):
    user: User
    doctor_profile: Optional[Doctor] = None
    permissions: List[str]
    is_online: bool

class DoctorPublicProfile(BaseModel):
    id: str
    first_name: str
    last_name: str
    specialty: DoctorSpecialty
    sub_specialties: List[DoctorSpecialty]
    years_of_experience: int
    rating: float
    total_reviews: int
    consultation_fee: str
    schedule: List[DoctorSchedule]
    bio: Optional[str]
    languages_spoken: List[str]

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse
    expires_at: datetime

class UserStatistics(BaseModel):
    total_users: int
    active_users: int
    total_doctors: int
    active_doctors: int
    users_by_role: Dict[str, int]
    users_by_status: Dict[str, int]
    doctors_by_specialty: Dict[str, int]

# Stockage en mémoire
users_db: Dict[str, User] = {}
doctors_db: Dict[str, Doctor] = {}
sessions_db: Dict[str, UserSession] = {}
refresh_tokens_db: Dict[str, RefreshToken] = {}

# Configuration de sécurité
security = HTTPBearer()
SECRET_KEY = "your-secret-key-change-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 heures
REFRESH_TOKEN_EXPIRE_DAYS = 7
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30

# Fonctions utilitaires de sécurité
def generate_id() -> str:
    """Génère un ID unique."""
    return str(uuid.uuid4())

def generate_salt() -> str:
    """Génère un salt aléatoire pour le hachage des mots de passe."""
    return secrets.token_hex(32)

def hash_password(password: str, salt: str) -> str:
    """Hache un mot de passe avec un salt."""
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def verify_password(password: str, salt: str, password_hash: str) -> bool:
    """Vérifie un mot de passe."""
    return hash_password(password, salt) == password_hash

def generate_token() -> str:
    """Génère un token sécurisé."""
    return secrets.token_urlsafe(32)

def create_access_token(user_id: str) -> tuple[str, datetime]:
    """Crée un token d'accès."""
    expires_at = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = generate_token()

    # Créer une session
    session = UserSession(
        session_id=generate_id(),
        user_id=user_id,
        created_at=datetime.now(),
        expires_at=expires_at,
        ip_address="127.0.0.1",  # À récupérer de la requête
        user_agent="API Client"   # À récupérer de la requête
    )

    sessions_db[token] = session
    return token, expires_at

def create_refresh_token(user_id: str) -> str:
    """Crée un token de rafraîchissement."""
    token = generate_token()
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    refresh_token = RefreshToken(
        token_id=generate_id(),
        user_id=user_id,
        token_hash=token_hash,
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    refresh_tokens_db[token] = refresh_token
    return token

def get_default_permissions(role: UserRole) -> UserPermissions:
    """Retourne les permissions par défaut selon le rôle."""
    if role == UserRole.ADMIN:
        return UserPermissions(
            can_view_patients=True,
            can_create_patients=True,
            can_edit_patients=True,
            can_delete_patients=True,
            can_view_scans=True,
            can_create_scans=True,
            can_view_treatments=True,
            can_create_treatments=True,
            can_view_appointments=True,
            can_create_appointments=True,
            can_manage_users=True,
            can_view_reports=True
        )
    elif role == UserRole.DOCTOR:
        return UserPermissions(
            can_view_patients=True,
            can_create_patients=True,
            can_edit_patients=True,
            can_view_scans=True,
            can_create_scans=True,
            can_view_treatments=True,
            can_create_treatments=True,
            can_view_appointments=True,
            can_create_appointments=True,
            can_view_reports=True
        )
    elif role == UserRole.NURSE:
        return UserPermissions(
            can_view_patients=True,
            can_edit_patients=True,
            can_view_scans=True,
            can_view_treatments=True,
            can_view_appointments=True,
            can_create_appointments=True
        )
    elif role == UserRole.TECHNICIAN:
        return UserPermissions(
            can_view_patients=True,
            can_view_scans=True,
            can_create_scans=True
        )
    elif role == UserRole.RECEPTIONIST:
        return UserPermissions(
            can_view_patients=True,
            can_create_patients=True,
            can_edit_patients=True,
            can_view_appointments=True,
            can_create_appointments=True
        )
    else:
        return UserPermissions()

def get_permissions_list(permissions: UserPermissions) -> List[str]:
    """Convertit les permissions en liste de chaînes."""
    perms = []
    if permissions.can_view_patients: perms.append("view_patients")
    if permissions.can_create_patients: perms.append("create_patients")
    if permissions.can_edit_patients: perms.append("edit_patients")
    if permissions.can_delete_patients: perms.append("delete_patients")
    if permissions.can_view_scans: perms.append("view_scans")
    if permissions.can_create_scans: perms.append("create_scans")
    if permissions.can_view_treatments: perms.append("view_treatments")
    if permissions.can_create_treatments: perms.append("create_treatments")
    if permissions.can_view_appointments: perms.append("view_appointments")
    if permissions.can_create_appointments: perms.append("create_appointments")
    if permissions.can_manage_users: perms.append("manage_users")
    if permissions.can_view_reports: perms.append("view_reports")
    perms.extend(permissions.custom_permissions)
    return perms

def is_user_online(user_id: str) -> bool:
    """Vérifie si un utilisateur est en ligne."""
    now = datetime.now()
    for session in sessions_db.values():
        if (session.user_id == user_id and
            session.is_active and
            session.expires_at > now):
            return True
    return False

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> User:
    """Récupère l'utilisateur actuel à partir du token."""
    token = credentials.credentials

    if token not in sessions_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )

    session = sessions_db[token]

    if not session.is_active or session.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expirée"
        )

    if session.user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé"
        )

    user = users_db[session.user_id]

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte utilisateur inactif"
        )

    # Mettre à jour la dernière activité
    session.last_activity = datetime.now()
    user.last_activity = datetime.now()

    return user

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API de Gestion des Utilisateurs et Médecins",
    description="API complète pour la gestion des utilisateurs, médecins et authentification.",
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
        "message": "API de Gestion des Utilisateurs et Médecins",
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
        "users_count": len(users_db),
        "doctors_count": len(doctors_db),
        "active_sessions": len([s for s in sessions_db.values() if s.is_active])
    }
