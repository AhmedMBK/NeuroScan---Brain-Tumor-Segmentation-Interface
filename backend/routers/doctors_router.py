"""
🧠 CereBloom - Router Médecins
Endpoints pour la gestion des médecins
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging

from config.database import get_database
from services.auth_service import AuthService
from models.api_models import BaseResponse, DoctorCreate, DoctorResponse
from models.database_models import User, Doctor

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Dépendance pour récupérer l'utilisateur actuel
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    auth_service = AuthService()
    user = await auth_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )
    return user

@router.get("/")
async def get_doctors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère la liste des médecins avec profils complets"""
    try:
        result = await db.execute(
            select(Doctor, User).join(User, Doctor.user_id == User.id).where(
                User.status == "ACTIVE",
                User.role == "DOCTOR"
            )
        )
        doctors_data = result.all()

        doctors_list = []
        for doctor, user in doctors_data:
            doctors_list.append({
                "id": doctor.id,
                "user_id": doctor.user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "bio": doctor.bio,
                "office_location": doctor.office_location,
                "is_active": doctor.is_active
            })

        return {"doctors": doctors_list}

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des médecins: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.get("/statistics")
async def get_doctors_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère les statistiques des médecins"""
    try:
        from sqlalchemy import func, case

        # Compter tous les utilisateurs avec le rôle DOCTOR
        total_doctors_query = await db.execute(
            select(func.count(User.id)).where(User.role == "DOCTOR")
        )
        total_doctors = total_doctors_query.scalar() or 0

        # Compter les médecins avec profil complété
        completed_profiles_query = await db.execute(
            select(func.count(Doctor.id))
        )
        completed_profiles = completed_profiles_query.scalar() or 0

        # Compter les médecins actifs (avec profil ET statut actif)
        active_doctors_query = await db.execute(
            select(func.count(Doctor.id)).join(User, Doctor.user_id == User.id).where(
                User.status == "ACTIVE",
                Doctor.is_active == True
            )
        )
        active_doctors = active_doctors_query.scalar() or 0

        return {
            "total_doctors": total_doctors,
            "completed_profiles": completed_profiles,
            "active_doctors": active_doctors,
            "pending_profiles": total_doctors - completed_profiles
        }

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        # Retourner des statistiques vides au lieu d'une erreur
        return {
            "total_doctors": 0,
            "completed_profiles": 0,
            "active_doctors": 0,
            "pending_profiles": 0
        }

@router.post("/complete-profile", response_model=DoctorResponse)
async def complete_doctor_profile(
    doctor_data: DoctorCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Complète le profil médecin lors de la première connexion"""
    try:
        import uuid
        from datetime import datetime

        # Vérifier que l'utilisateur est un docteur
        if current_user.role.value != "DOCTOR":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les utilisateurs avec le rôle DOCTOR peuvent compléter ce profil"
            )

        # Vérifier qu'il n'a pas déjà un profil médecin
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Profil médecin déjà complété"
            )

        # Création du profil médecin
        doctor = Doctor(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            bio=doctor_data.bio,
            office_location=doctor_data.office_location,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(doctor)
        await db.commit()
        await db.refresh(doctor)

        logger.info(f"Profil médecin complété par {current_user.email}: {doctor.id}")

        return DoctorResponse.model_validate(doctor)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erreur lors de la complétion du profil médecin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la complétion du profil médecin: {str(e)}"
        )

@router.get("/profile/status")
async def check_profile_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Vérifie si l'utilisateur docteur a complété son profil"""
    try:
        if current_user.role.value != "DOCTOR":
            return {"has_profile": False, "message": "Utilisateur non-docteur"}

        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor = result.scalar_one_or_none()

        return {
            "has_profile": doctor is not None,
            "doctor_id": doctor.id if doctor else None,
            "message": "Profil complété" if doctor else "Profil à compléter"
        }

    except Exception as e:
        logger.error(f"Erreur lors de la vérification du profil: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.get("/my-secretaries")
async def get_my_secretaries(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère la liste des secrétaires assignées au médecin connecté"""
    try:
        # Vérifier que l'utilisateur est un médecin
        if current_user.role.value != "DOCTOR":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les médecins peuvent consulter leurs secrétaires"
            )

        # Récupérer le profil médecin
        doctor_result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor_profile = doctor_result.scalar_one_or_none()

        if not doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Profil médecin non trouvé. Complétez votre profil d'abord."
            )

        # Récupérer les secrétaires assignées à ce médecin
        result = await db.execute(
            select(User).where(
                User.role == "SECRETARY",
                User.assigned_doctor_id == doctor_profile.id
            )
        )
        secretaries = result.scalars().all()

        secretaries_list = []
        for secretary in secretaries:
            secretaries_list.append({
                "id": secretary.id,
                "first_name": secretary.first_name,
                "last_name": secretary.last_name,
                "email": secretary.email,
                "phone": secretary.phone,
                "employee_id": secretary.employee_id,
                "status": secretary.status.value,
                "created_at": secretary.created_at.isoformat()
            })

        return {
            "doctor_id": doctor_profile.id,
            "doctor_name": f"{current_user.first_name} {current_user.last_name}",
            "secretaries_count": len(secretaries_list),
            "secretaries": secretaries_list
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des secrétaires: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des secrétaires"
        )

@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(
    doctor_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère un médecin par son ID"""
    try:
        result = await db.execute(
            select(Doctor).where(Doctor.id == doctor_id)
        )
        doctor = result.scalar_one_or_none()

        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Médecin non trouvé"
            )

        return DoctorResponse.model_validate(doctor)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du médecin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/create-secretary", response_model=dict)
async def create_secretary(
    secretary_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Permet à un médecin de créer une secrétaire qui lui sera automatiquement assignée"""
    try:
        import uuid
        from models.database_models import UserCredentials, UserPermissions
        from services.auth_service import AuthService
        from services.employee_id_service import async_validate_or_generate_employee_id
        from config.settings import USER_ROLE_PERMISSIONS

        # Vérifier que l'utilisateur est un médecin
        if current_user.role.value != "DOCTOR":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les médecins peuvent créer des secrétaires"
            )

        # Récupérer le profil médecin
        doctor_result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor_profile = doctor_result.scalar_one_or_none()

        if not doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Profil médecin non trouvé. Complétez votre profil d'abord."
            )

        # Validation des données requises
        required_fields = ['first_name', 'last_name', 'email', 'username', 'password']
        for field in required_fields:
            if field not in secretary_data or not secretary_data[field]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Le champ '{field}' est requis"
                )

        # Vérifier que l'email n'existe pas
        result = await db.execute(
            select(User).where(User.email == secretary_data['email'])
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec cet email existe déjà"
            )

        # Vérifier que le username n'existe pas
        result = await db.execute(
            select(UserCredentials).where(UserCredentials.username == secretary_data['username'])
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce nom d'utilisateur existe déjà"
            )

        # Génération automatique de l'employee_id
        employee_id = await async_validate_or_generate_employee_id(
            db,
            None,  # Génération automatique
            "SECRETARY"
        )

        # Création de la secrétaire
        user_id = str(uuid.uuid4())
        secretary_user = User(
            id=user_id,
            first_name=secretary_data['first_name'],
            last_name=secretary_data['last_name'],
            email=secretary_data['email'],
            phone=secretary_data.get('phone'),
            role="SECRETARY",
            status="ACTIVE",
            employee_id=employee_id,
            assigned_doctor_id=doctor_profile.id,  # Assignation automatique au médecin
            created_by=current_user.id
        )

        # Création des credentials
        auth_service = AuthService()
        password_hash, salt = auth_service.hash_password(secretary_data['password'])
        credentials = UserCredentials(
            user_id=user_id,
            username=secretary_data['username'],
            password_hash=password_hash,
            salt=salt
        )

        # Création des permissions par défaut pour secrétaire
        role_permissions = USER_ROLE_PERMISSIONS.get("SECRETARY", {})
        permissions = UserPermissions(
            user_id=user_id,
            can_view_patients=role_permissions.get("can_view_patients", False),
            can_create_patients=role_permissions.get("can_create_patients", False),
            can_edit_patients=role_permissions.get("can_edit_patients", False),
            can_delete_patients=role_permissions.get("can_delete_patients", False),
            can_view_segmentations=role_permissions.get("can_view_segmentations", False),
            can_create_segmentations=role_permissions.get("can_create_segmentations", False),
            can_validate_segmentations=role_permissions.get("can_validate_segmentations", False),
            can_manage_appointments=role_permissions.get("can_manage_appointments", False),
            can_manage_users=role_permissions.get("can_manage_users", False),
            can_view_reports=role_permissions.get("can_view_reports", False),
            can_export_data=role_permissions.get("can_export_data", False)
        )

        db.add(secretary_user)
        db.add(credentials)
        db.add(permissions)
        await db.commit()

        logger.info(f"Secrétaire créée par Dr. {current_user.email}: {secretary_user.email} (assignée au Dr. ID: {doctor_profile.id})")

        return {
            "message": "Secrétaire créée avec succès",
            "secretary": {
                "id": secretary_user.id,
                "first_name": secretary_user.first_name,
                "last_name": secretary_user.last_name,
                "email": secretary_user.email,
                "employee_id": secretary_user.employee_id,
                "assigned_doctor_id": secretary_user.assigned_doctor_id,
                "username": secretary_data['username']
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la création de la secrétaire: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de la secrétaire"
        )


