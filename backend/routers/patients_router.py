"""
🧠 CereBloom - Router Patients
Endpoints pour la gestion des patients
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
from models.api_models import BaseResponse, PatientCreate, PatientUpdate, PatientResponse
from models.database_models import User, Patient, Doctor

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
async def get_patients(
    page: int = 1,
    size: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère la liste des patients avec pagination et filtrage par rôle"""
    try:
        from sqlalchemy import func

        # Calculer l'offset
        offset = (page - 1) * size

        # Construire la requête selon le rôle de l'utilisateur avec jointure pour récupérer les infos du médecin
        base_query = select(Patient).options(
            selectinload(Patient.assigned_doctor).selectinload(Doctor.user)
        )
        count_query = select(func.count(Patient.id))

        if current_user.role.value == "ADMIN":
            # ADMIN : Voir tous les patients
            logger.info(f"Admin {current_user.email} accède à tous les patients")

        elif current_user.role.value == "DOCTOR":
            # DOCTOR : Voir uniquement ses patients assignés
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

            # Filtrer par assigned_doctor_id
            base_query = base_query.where(Patient.assigned_doctor_id == doctor_profile.id)
            count_query = count_query.where(Patient.assigned_doctor_id == doctor_profile.id)

            logger.info(f"Médecin {current_user.email} (ID: {doctor_profile.id}) accède à ses patients")

        elif current_user.role.value == "SECRETARY":
            # SECRETARY : Voir uniquement les patients de son médecin assigné
            if not current_user.assigned_doctor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Secrétaire non assignée à un médecin. Contactez l'administrateur."
                )

            # Filtrer par le médecin assigné à la secrétaire
            base_query = base_query.where(Patient.assigned_doctor_id == current_user.assigned_doctor_id)
            count_query = count_query.where(Patient.assigned_doctor_id == current_user.assigned_doctor_id)

            logger.info(f"Secrétaire {current_user.email} accède aux patients du Dr. ID: {current_user.assigned_doctor_id}")

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rôle non autorisé à accéder aux patients"
            )

        # Compter le total avec filtre
        count_result = await db.execute(count_query)
        total = count_result.scalar()

        # Récupérer les patients avec pagination et filtre
        result = await db.execute(
            base_query
            .offset(offset)
            .limit(size)
            .order_by(Patient.created_at.desc())
        )
        patients = result.scalars().all()

        # Convertir en PatientResponse avec sérialisation manuelle
        patient_responses = []
        for p in patients:
            patient_dict = {
                "id": str(p.id),
                "first_name": p.first_name,
                "last_name": p.last_name,
                "date_of_birth": p.date_of_birth,
                "gender": p.gender,
                "email": p.email,
                "phone": p.phone,
                "address": p.address,
                "blood_type": p.blood_type,
                "height": p.height,
                "weight": p.weight,
                "emergency_contact": p.emergency_contact,
                "assigned_doctor_id": str(p.assigned_doctor_id) if p.assigned_doctor_id else None,
                "medical_history": p.medical_history,
                "notes": p.notes,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "assigned_doctor": None
            }

            # Ajouter les informations du médecin assigné si disponible
            if p.assigned_doctor and p.assigned_doctor.user:
                patient_dict["assigned_doctor"] = {
                    "id": str(p.assigned_doctor.id),
                    "user": {
                        "id": str(p.assigned_doctor.user.id),
                        "first_name": p.assigned_doctor.user.first_name,
                        "last_name": p.assigned_doctor.user.last_name,
                        "email": p.assigned_doctor.user.email
                    }
                }

            patient_responses.append(patient_dict)

        # Calculer le nombre de pages
        pages = (total + size - 1) // size

        logger.info(f"Utilisateur {current_user.email} ({current_user.role.value}) récupère {len(patients)} patients (page {page}/{pages})")

        return {
            "items": patient_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des patients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Crée un nouveau patient"""
    try:
        import uuid
        from datetime import datetime

        # Vérification des permissions (Docteur, Admin ou Secrétaire peuvent créer des patients)
        if current_user.role.value not in ["ADMIN", "DOCTOR", "SECRETARY"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes pour créer un patient"
            )

        # Déterminer l'assigned_doctor_id selon le rôle
        assigned_doctor_id = None

        if current_user.role.value == "DOCTOR":
            # DOCTOR : Assigner automatiquement le patient au médecin créateur
            doctor_result = await db.execute(
                select(Doctor).where(Doctor.user_id == current_user.id)
            )
            doctor_profile = doctor_result.scalar_one_or_none()

            if not doctor_profile:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Profil médecin non trouvé. Complétez votre profil d'abord."
                )

            assigned_doctor_id = doctor_profile.id
            logger.info(f"Patient automatiquement assigné au Dr. {current_user.first_name} {current_user.last_name} (ID: {doctor_profile.id})")

        elif current_user.role.value == "SECRETARY":
            # SECRETARY : Assigner automatiquement le patient au médecin de la secrétaire
            if not current_user.assigned_doctor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Secrétaire non assignée à un médecin. Contactez l'administrateur."
                )

            assigned_doctor_id = current_user.assigned_doctor_id
            logger.info(f"Patient automatiquement assigné au médecin de la secrétaire (ID: {assigned_doctor_id})")

        elif current_user.role.value == "ADMIN":
            # ADMIN : Utiliser l'assigned_doctor_id fourni dans le formulaire (peut être None)
            assigned_doctor_id = patient_data.assigned_doctor_id
            logger.info(f"Admin assigne le patient au médecin ID: {assigned_doctor_id or 'Aucun'}")

        # Vérification si l'email existe déjà (si fourni)
        if patient_data.email:
            result = await db.execute(
                select(Patient).where(Patient.email == patient_data.email)
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Un patient avec cet email existe déjà"
                )

        # Conversion de la date de naissance
        from datetime import datetime
        try:
            date_of_birth = datetime.strptime(patient_data.date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de date invalide. Utilisez YYYY-MM-DD"
            )

        # Création du patient
        patient = Patient(
            id=str(uuid.uuid4()),
            first_name=patient_data.first_name,
            last_name=patient_data.last_name,
            date_of_birth=date_of_birth,
            gender=patient_data.gender,
            email=patient_data.email,
            phone=patient_data.phone,
            address=patient_data.address,
            blood_type=patient_data.blood_type,
            height=patient_data.height,
            weight=patient_data.weight,
            emergency_contact={
                "name": patient_data.emergency_contact_name,
                "phone": patient_data.emergency_contact_phone,
                "relationship": patient_data.emergency_contact_relationship
            } if patient_data.emergency_contact_name or patient_data.emergency_contact_phone or patient_data.emergency_contact_relationship else None,
            assigned_doctor_id=assigned_doctor_id,
            medical_history={
                "history": patient_data.medical_history,
                "allergies": patient_data.allergies,
                "current_medications": patient_data.current_medications,
                "insurance_number": patient_data.insurance_number
            } if any([patient_data.medical_history, patient_data.allergies, patient_data.current_medications, patient_data.insurance_number]) else None,
            notes=patient_data.notes,
            created_by_user_id=current_user.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(patient)

        try:
            await db.commit()
            await db.refresh(patient)
        except Exception as commit_error:
            await db.rollback()
            logger.error(f"Erreur lors du commit: {commit_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la sauvegarde: {str(commit_error)}"
            )

        logger.info(f"Patient créé par {current_user.email}: {patient.first_name} {patient.last_name}")

        return PatientResponse.model_validate(patient)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erreur lors de la création du patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du patient: {str(e)}"
        )

@router.get("/statistics")
async def get_patients_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère les statistiques des patients avec filtrage par rôle"""
    try:
        from sqlalchemy import func, case
        from models.database_models import Gender

        # Construire la requête selon le rôle de l'utilisateur
        base_query = select(Patient)

        if current_user.role.value == "ADMIN":
            # ADMIN : Voir tous les patients
            logger.info(f"Admin {current_user.email} accède aux statistiques de tous les patients")

        elif current_user.role.value == "DOCTOR":
            # DOCTOR : Voir uniquement ses patients assignés
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

            # Filtrer par assigned_doctor_id
            base_query = base_query.where(Patient.assigned_doctor_id == doctor_profile.id)
            logger.info(f"Médecin {current_user.email} (ID: {doctor_profile.id}) accède aux statistiques de ses patients")

        elif current_user.role.value == "SECRETARY":
            # SECRETARY : Voir uniquement les patients de son médecin assigné
            if not current_user.assigned_doctor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Secrétaire non assignée à un médecin. Contactez l'administrateur."
                )

            # Filtrer par le médecin assigné à la secrétaire
            base_query = base_query.where(Patient.assigned_doctor_id == current_user.assigned_doctor_id)
            logger.info(f"Secrétaire {current_user.email} accède aux statistiques des patients du Dr. ID: {current_user.assigned_doctor_id}")

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rôle non autorisé à accéder aux statistiques des patients"
            )

        # Statistiques générales avec filtrage
        # Construire la requête de statistiques avec les mêmes filtres
        stats_select = select(
            func.count(Patient.id).label("total_patients"),
            func.count(case((Patient.gender == Gender.MALE, 1))).label("male_patients"),
            func.count(case((Patient.gender == Gender.FEMALE, 1))).label("female_patients")
        )

        # Appliquer les mêmes filtres que base_query
        if current_user.role.value == "DOCTOR":
            stats_select = stats_select.where(Patient.assigned_doctor_id == doctor_profile.id)
        elif current_user.role.value == "SECRETARY":
            stats_select = stats_select.where(Patient.assigned_doctor_id == current_user.assigned_doctor_id)

        stats_query = await db.execute(stats_select)
        stats = stats_query.first()

        return {
            "total_patients": stats.total_patients or 0,
            "male_patients": stats.male_patients or 0,
            "female_patients": stats.female_patients or 0,
            "patients_by_gender": {
                "male": stats.male_patients or 0,
                "female": stats.female_patients or 0
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        # Retourner des statistiques vides au lieu d'une erreur
        return {
            "total_patients": 0,
            "male_patients": 0,
            "female_patients": 0,
            "patients_by_gender": {
                "male": 0,
                "female": 0
            }
        }

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère un patient par son ID avec vérification des permissions"""
    try:
        result = await db.execute(
            select(Patient).options(
                selectinload(Patient.assigned_doctor).selectinload(Doctor.user)
            ).where(Patient.id == patient_id)
        )
        patient = result.scalar_one_or_none()

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient non trouvé"
            )

        # Vérification des permissions selon le rôle
        if current_user.role.value == "ADMIN":
            # ADMIN : Accès à tous les patients
            pass

        elif current_user.role.value == "DOCTOR":
            # DOCTOR : Accès uniquement à ses patients assignés
            doctor_result = await db.execute(
                select(Doctor).where(Doctor.user_id == current_user.id)
            )
            doctor_profile = doctor_result.scalar_one_or_none()

            if not doctor_profile:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Profil médecin non trouvé"
                )

            if patient.assigned_doctor_id != doctor_profile.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Accès refusé : ce patient n'est pas assigné à ce médecin"
                )

        elif current_user.role.value == "SECRETARY":
            # SECRETARY : Accès uniquement aux patients de son médecin assigné
            if not current_user.assigned_doctor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Secrétaire non assignée à un médecin"
                )

            if patient.assigned_doctor_id != current_user.assigned_doctor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Accès refusé : ce patient n'est pas assigné au médecin de cette secrétaire"
                )

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rôle non autorisé"
            )

        logger.info(f"Utilisateur {current_user.email} ({current_user.role.value}) accède au patient {patient.first_name} {patient.last_name}")

        # Sérialisation manuelle avec informations du médecin
        patient_dict = {
            "id": str(patient.id),
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender,
            "email": patient.email,
            "phone": patient.phone,
            "address": patient.address,
            "blood_type": patient.blood_type,
            "height": patient.height,
            "weight": patient.weight,
            "emergency_contact": patient.emergency_contact,
            "assigned_doctor_id": str(patient.assigned_doctor_id) if patient.assigned_doctor_id else None,
            "medical_history": patient.medical_history,
            "notes": patient.notes,
            "created_at": patient.created_at,
            "updated_at": patient.updated_at,
            "assigned_doctor": None
        }

        # Ajouter les informations du médecin assigné si disponible
        if patient.assigned_doctor and patient.assigned_doctor.user:
            patient_dict["assigned_doctor"] = {
                "id": str(patient.assigned_doctor.id),
                "user": {
                    "id": str(patient.assigned_doctor.user.id),
                    "first_name": patient.assigned_doctor.user.first_name,
                    "last_name": patient.assigned_doctor.user.last_name,
                    "email": patient.assigned_doctor.user.email
                }
            }

        return patient_dict

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Met à jour un patient"""
    try:
        # Vérification des permissions
        if current_user.role.value not in ["ADMIN", "DOCTOR", "SECRETARY"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes pour modifier un patient"
            )

        # Récupérer le patient existant
        result = await db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        patient = result.scalar_one_or_none()

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient non trouvé"
            )

        # Mettre à jour les champs modifiés
        from datetime import datetime

        if patient_data.first_name is not None:
            patient.first_name = patient_data.first_name
        if patient_data.last_name is not None:
            patient.last_name = patient_data.last_name
        if patient_data.email is not None:
            patient.email = patient_data.email
        if patient_data.phone is not None:
            patient.phone = patient_data.phone
        if patient_data.address is not None:
            patient.address = patient_data.address
        if patient_data.blood_type is not None:
            patient.blood_type = patient_data.blood_type
        if patient_data.height is not None:
            patient.height = patient_data.height
        if patient_data.weight is not None:
            patient.weight = patient_data.weight
        if patient_data.assigned_doctor_id is not None:
            patient.assigned_doctor_id = patient_data.assigned_doctor_id
        if patient_data.notes is not None:
            patient.notes = patient_data.notes

        # Mettre à jour le contact d'urgence
        if any([patient_data.emergency_contact_name, patient_data.emergency_contact_phone, patient_data.emergency_contact_relationship]):
            patient.emergency_contact = {
                "name": patient_data.emergency_contact_name,
                "phone": patient_data.emergency_contact_phone,
                "relationship": patient_data.emergency_contact_relationship
            }

        # Mettre à jour l'historique médical
        if patient_data.medical_history is not None or patient_data.allergies is not None:
            current_history = patient.medical_history or {}
            if patient_data.medical_history is not None:
                current_history["history"] = patient_data.medical_history
            if patient_data.allergies is not None:
                current_history["allergies"] = patient_data.allergies
            patient.medical_history = current_history

        patient.updated_at = datetime.now()

        await db.commit()
        await db.refresh(patient)

        logger.info(f"Patient modifié par {current_user.email}: {patient.first_name} {patient.last_name}")

        return PatientResponse.model_validate(patient)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erreur lors de la modification du patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )