"""
🧠 CereBloom - Router Rendez-vous
Endpoints pour la gestion des rendez-vous
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import logging

from config.database import get_database
from services.auth_service import AuthService
from models.api_models import BaseResponse, AppointmentCreate, AppointmentResponse
from models.database_models import User, Appointment, Patient, Doctor

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
async def get_appointments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère la liste des rendez-vous avec filtrage par rôle"""
    try:
        from models.database_models import Doctor

        # Construire la requête selon le rôle de l'utilisateur avec jointures pour récupérer patient et médecin
        base_query = select(Appointment).options(
            selectinload(Appointment.patient),
            selectinload(Appointment.doctor).selectinload(Doctor.user)
        )

        if current_user.role.value == "ADMIN":
            # ADMIN : Voir tous les rendez-vous
            logger.info(f"Admin {current_user.email} accède à tous les rendez-vous")

        elif current_user.role.value == "DOCTOR":
            # DOCTOR : Voir uniquement ses rendez-vous
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

            # Filtrer par doctor_id
            base_query = base_query.where(Appointment.doctor_id == doctor_profile.id)
            logger.info(f"Médecin {current_user.email} (ID: {doctor_profile.id}) accède à ses rendez-vous")

        elif current_user.role.value == "SECRETARY":
            # SECRETARY : Voir uniquement les rendez-vous de son médecin assigné
            if not current_user.assigned_doctor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Secrétaire non assignée à un médecin. Contactez l'administrateur."
                )

            # Filtrer par le médecin assigné à la secrétaire
            base_query = base_query.where(Appointment.doctor_id == current_user.assigned_doctor_id)
            logger.info(f"Secrétaire {current_user.email} accède aux rendez-vous du Dr. ID: {current_user.assigned_doctor_id}")

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rôle non autorisé à accéder aux rendez-vous"
            )

        # Exécuter la requête
        result = await db.execute(base_query.order_by(Appointment.appointment_date.desc()))
        appointments = result.scalars().all()

        # Formater les données de retour avec informations patient et médecin
        appointments_data = []
        for appointment in appointments:
            # Informations du patient
            patient_info = None
            if appointment.patient:
                patient_info = {
                    "id": appointment.patient.id,
                    "first_name": appointment.patient.first_name,
                    "last_name": appointment.patient.last_name,
                    "email": appointment.patient.email
                }

            # Informations du médecin
            doctor_info = None
            if appointment.doctor and appointment.doctor.user:
                doctor_info = {
                    "id": appointment.doctor.id,
                    "user": {
                        "id": appointment.doctor.user.id,
                        "first_name": appointment.doctor.user.first_name,
                        "last_name": appointment.doctor.user.last_name,
                        "email": appointment.doctor.user.email
                    }
                }

            appointments_data.append({
                "id": appointment.id,
                "patient_id": appointment.patient_id,
                "doctor_id": appointment.doctor_id,
                "appointment_date": appointment.appointment_date.isoformat() if appointment.appointment_date else None,
                "appointment_time": str(appointment.appointment_time) if appointment.appointment_time else None,
                "status": appointment.status.value if appointment.status else "SCHEDULED",
                "notes": appointment.notes,
                "appointment_type": appointment.appointment_type,
                "created_at": appointment.created_at.isoformat() if appointment.created_at else None,
                "patient": patient_info,
                "doctor": doctor_info
            })

        return {"appointments": appointments_data}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des rendez-vous: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Crée un nouveau rendez-vous"""
    try:
        import uuid
        from datetime import datetime

        # Vérification des permissions (Docteur, Admin ou Secrétaire)
        if current_user.role.value not in ["ADMIN", "DOCTOR", "SECRETARY"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes pour créer un rendez-vous"
            )

        # Création du rendez-vous
        appointment = Appointment(
            id=str(uuid.uuid4()),
            patient_id=appointment_data.patient_id,
            doctor_id=appointment_data.doctor_id,
            scheduled_by_user_id=current_user.id,
            appointment_date=appointment_data.appointment_date,
            appointment_time=appointment_data.appointment_time,
            status=appointment_data.status or "SCHEDULED",
            notes=appointment_data.notes,
            appointment_type=appointment_data.appointment_type,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(appointment)
        await db.commit()
        await db.refresh(appointment)

        logger.info(f"Rendez-vous créé par {current_user.email}: {appointment.appointment_date}")

        return AppointmentResponse.model_validate(appointment)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erreur lors de la création du rendez-vous: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du rendez-vous: {str(e)}"
        )

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère un rendez-vous par son ID"""
    try:
        result = await db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        appointment = result.scalar_one_or_none()

        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rendez-vous non trouvé"
            )

        return AppointmentResponse.model_validate(appointment)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du rendez-vous: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )
