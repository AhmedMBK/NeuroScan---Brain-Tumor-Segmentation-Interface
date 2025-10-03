"""
🧠 CereBloom - Router Utilisateurs
Endpoints pour la gestion des utilisateurs
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging
import uuid

from config.database import get_database
from services.auth_service import AuthService
from services.employee_id_service import async_validate_or_generate_employee_id, AsyncEmployeeIdService
from models.api_models import (
    UserCreate, UserUpdate, UserResponse,
    BaseResponse, PaginatedResponse, PaginationParams
)
from models.database_models import User, UserCredentials, UserPermissions, Doctor
from config.settings import USER_ROLE_PERMISSIONS

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

@router.get("/", response_model=PaginatedResponse)
async def get_users(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère la liste des utilisateurs (Admin seulement)"""
    try:
        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès réservé aux administrateurs"
            )

        # Récupération avec pagination
        offset = (pagination.page - 1) * pagination.size

        result = await db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(pagination.size)
        )
        users = result.scalars().all()

        # Comptage total
        from sqlalchemy import func
        count_result = await db.execute(select(func.count(User.id)))
        total = count_result.scalar()

        return PaginatedResponse(
            items=[UserResponse.model_validate(user) for user in users],
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Crée un nouvel utilisateur (Admin seulement)"""
    try:
        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès réservé aux administrateurs"
            )

        # Vérification que l'email n'existe pas
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec cet email existe déjà"
            )

        # Vérification que le username n'existe pas
        result = await db.execute(
            select(UserCredentials).where(UserCredentials.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce nom d'utilisateur existe déjà"
            )

        # Validation de assigned_doctor_id selon le rôle
        if user_data.assigned_doctor_id:
            if user_data.role != "SECRETARY":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Seules les secrétaires peuvent être assignées à un médecin"
                )

            # Vérifier que le médecin existe
            doctor_result = await db.execute(
                select(Doctor).where(Doctor.id == user_data.assigned_doctor_id)
            )
            if not doctor_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Le médecin assigné n'existe pas"
                )
        elif user_data.role == "SECRETARY":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Une secrétaire doit être assignée à un médecin"
            )

        # Génération automatique de l'employee_id si nécessaire
        try:
            employee_id = await async_validate_or_generate_employee_id(
                db,
                getattr(user_data, 'employee_id', None),
                user_data.role
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Création de l'utilisateur
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            phone=user_data.phone,
            role=user_data.role,
            status="ACTIVE",
            employee_id=employee_id,
            assigned_doctor_id=user_data.assigned_doctor_id,
            created_by=current_user.id
        )

        # Création des credentials
        auth_service = AuthService()
        password_hash, salt = auth_service.hash_password(user_data.password)
        credentials = UserCredentials(
            user_id=user_id,
            username=user_data.username,
            password_hash=password_hash,
            salt=salt
        )

        # Création des permissions par défaut
        role_permissions = USER_ROLE_PERMISSIONS.get(user_data.role.value, {})
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

        db.add(user)
        db.add(credentials)
        db.add(permissions)
        await db.commit()

        logger.info(f"Utilisateur créé par {current_user.email}: {user.email}")

        return UserResponse.model_validate(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la création d'utilisateur: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de l'utilisateur"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère un utilisateur par son ID"""
    try:
        # Vérification des permissions
        if current_user.role != "ADMIN" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès refusé"
            )

        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )

        return UserResponse.model_validate(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Met à jour un utilisateur"""
    try:
        # Vérification des permissions
        if current_user.role != "ADMIN" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès refusé"
            )

        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )

        # Validation de assigned_doctor_id si modifié
        if hasattr(user_data, 'assigned_doctor_id') and user_data.assigned_doctor_id is not None:
            if user.role != "SECRETARY":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Seules les secrétaires peuvent être assignées à un médecin"
                )

            # Vérifier que le médecin existe
            doctor_result = await db.execute(
                select(Doctor).where(Doctor.id == user_data.assigned_doctor_id)
            )
            if not doctor_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Le médecin assigné n'existe pas"
                )

        # Mise à jour des champs
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()

        logger.info(f"Utilisateur mis à jour par {current_user.email}: {user.email}")

        return UserResponse.model_validate(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour"
        )

@router.delete("/{user_id}", response_model=BaseResponse)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Supprime un utilisateur (Admin seulement)"""
    try:
        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès réservé aux administrateurs"
            )

        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de supprimer son propre compte"
            )

        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )

        await db.delete(user)
        await db.commit()

        logger.info(f"Utilisateur supprimé par {current_user.email}: {user.email}")

        return BaseResponse(message="Utilisateur supprimé avec succès")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression"
        )

@router.get("/employee-id/statistics")
async def get_employee_id_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Obtient les statistiques des employee_id (Admin seulement)"""
    try:
        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès réservé aux administrateurs"
            )

        stats = await AsyncEmployeeIdService.get_role_statistics(db)

        return {
            "message": "Statistiques des employee_id récupérées",
            "data": stats
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )
