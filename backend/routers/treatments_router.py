"""
🧠 CereBloom - Router Traitements
Endpoints pour la gestion des traitements
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
from models.api_models import BaseResponse, TreatmentCreate, TreatmentResponse
from models.database_models import User, Treatment

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
async def get_treatments(
    patient_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère la liste des traitements avec filtrage par patient et rôle"""
    try:
        from models.database_models import Doctor, Patient

        # Construire la requête selon le rôle de l'utilisateur avec jointure pour récupérer les infos du médecin prescripteur
        base_query = select(Treatment).options(
            selectinload(Treatment.prescribed_by_doctor).selectinload(Doctor.user)
        )

        if current_user.role.value == "ADMIN":
            # ADMIN : Voir tous les traitements
            logger.info(f"Admin {current_user.email} accède à tous les traitements")

        elif current_user.role.value == "DOCTOR":
            # DOCTOR : Voir uniquement les traitements de ses patients assignés
            doctor_result = await db.execute(
                select(Doctor).where(Doctor.user_id == current_user.id)
            )
            doctor_profile = doctor_result.scalar_one_or_none()

            if not doctor_profile:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Profil médecin non trouvé. Complétez votre profil d'abord."
                )

            # Filtrer via les patients assignés au médecin
            base_query = base_query.join(Patient, Treatment.patient_id == Patient.id).where(
                Patient.assigned_doctor_id == doctor_profile.id
            )
            logger.info(f"Médecin {current_user.email} accède aux traitements de ses patients")

        elif current_user.role.value == "SECRETARY":
            # SECRETARY : Voir uniquement les traitements des patients de son médecin assigné
            if not current_user.assigned_doctor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Secrétaire non assignée à un médecin. Contactez l'administrateur."
                )

            # Filtrer via les patients assignés au médecin de la secrétaire
            base_query = base_query.join(Patient, Treatment.patient_id == Patient.id).where(
                Patient.assigned_doctor_id == current_user.assigned_doctor_id
            )
            logger.info(f"Secrétaire {current_user.email} accède aux traitements du Dr. ID: {current_user.assigned_doctor_id}")

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rôle non autorisé à accéder aux traitements"
            )

        # Filtrer par patient si spécifié
        if patient_id:
            base_query = base_query.where(Treatment.patient_id == patient_id)
            logger.info(f"Filtrage par patient: {patient_id}")

        # Exécuter la requête
        result = await db.execute(base_query.order_by(Treatment.start_date.desc()))
        treatments = result.scalars().all()

        # Retourner les données complètes avec informations du médecin prescripteur
        treatments_data = []
        for t in treatments:
            # Récupérer les informations du médecin prescripteur
            doctor_name = "Non spécifié"
            if t.prescribed_by_doctor and t.prescribed_by_doctor.user:
                doctor_name = f"Dr. {t.prescribed_by_doctor.user.first_name} {t.prescribed_by_doctor.user.last_name}"

            treatments_data.append({
                "id": t.id,
                "patient_id": t.patient_id,
                "prescribed_by_doctor_id": t.prescribed_by_doctor_id,
                "doctor": doctor_name,  # Nom complet du médecin pour le frontend
                "doctor_name": doctor_name,  # Alias pour compatibilité
                "treatment_type": t.treatment_type,
                "treatment_name": t.medication_name or t.treatment_type,  # Compatibilité frontend
                "medication_name": t.medication_name,
                "dosage": t.dosage,
                "frequency": t.frequency,
                "duration": t.duration,
                "start_date": t.start_date.isoformat() if t.start_date else None,
                "end_date": t.end_date.isoformat() if t.end_date else None,
                "status": t.status.value if t.status else "ACTIVE",
                "notes": t.notes,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None
            })

        return {"treatments": treatments_data}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des traitements: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/", response_model=TreatmentResponse)
async def create_treatment(
    treatment_data: TreatmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Crée un nouveau traitement"""
    try:
        import uuid
        from datetime import datetime

        # Vérification des permissions (Docteur ou Admin)
        if current_user.role.value not in ["ADMIN", "DOCTOR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes pour créer un traitement"
            )

        # Création du traitement
        treatment = Treatment(
            id=str(uuid.uuid4()),
            patient_id=treatment_data.patient_id,
            prescribed_by_doctor_id=treatment_data.prescribed_by_doctor_id or current_user.id,
            treatment_type=treatment_data.treatment_type,
            medication_name=treatment_data.medication_name,
            dosage=treatment_data.dosage,
            frequency=treatment_data.frequency,
            duration=treatment_data.duration,
            start_date=treatment_data.start_date,
            end_date=treatment_data.end_date,
            status=treatment_data.status or "ACTIVE",
            notes=treatment_data.notes,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(treatment)
        await db.commit()
        await db.refresh(treatment)

        logger.info(f"Traitement créé par {current_user.email}: {treatment.treatment_type}")

        return TreatmentResponse.model_validate(treatment)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erreur lors de la création du traitement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du traitement: {str(e)}"
        )

@router.get("/{treatment_id}", response_model=TreatmentResponse)
async def get_treatment(
    treatment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère un traitement par son ID"""
    try:
        result = await db.execute(
            select(Treatment).where(Treatment.id == treatment_id)
        )
        treatment = result.scalar_one_or_none()

        if not treatment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Traitement non trouvé"
            )

        return TreatmentResponse.model_validate(treatment)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du traitement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )
