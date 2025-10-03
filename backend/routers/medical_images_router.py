"""
🧠 CereBloom - Router Images Médicales
Endpoints pour la gestion des images médicales
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import logging
import os
import uuid
import aiofiles
from pathlib import Path
from datetime import datetime

from config.database import get_database
from services.auth_service import AuthService
from models.api_models import BaseResponse, MedicalImageCreate, MedicalImageResponse
from models.database_models import User, MedicalImage

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
async def get_medical_images(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère la liste des images médicales"""
    try:
        result = await db.execute(select(MedicalImage))
        images = result.scalars().all()

        return {"images": [{"id": i.id, "file_name": i.file_name, "modality": i.modality} for i in images]}

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des images: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/", response_model=MedicalImageResponse)
async def create_medical_image(
    image_data: MedicalImageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Crée une nouvelle image médicale"""
    try:
        import uuid
        from datetime import datetime

        # Vérification des permissions (Docteur, Admin ou Secrétaire)
        if current_user.role.value not in ["ADMIN", "DOCTOR", "SECRETARY"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes pour créer une image médicale"
            )

        # Création de l'image médicale
        medical_image = MedicalImage(
            id=str(uuid.uuid4()),
            patient_id=image_data.patient_id,
            uploaded_by_user_id=current_user.id,
            modality=image_data.modality,
            file_path=image_data.file_path,
            file_name=image_data.file_name,
            file_size=image_data.file_size,
            image_metadata=image_data.metadata,
            acquisition_date=image_data.acquisition_date,
            body_part=image_data.body_part,
            notes=image_data.notes,
            is_processed=image_data.is_processed if image_data.is_processed is not None else False,
            dicom_metadata=image_data.dicom_metadata,
            uploaded_at=datetime.now()
        )

        db.add(medical_image)
        await db.commit()
        await db.refresh(medical_image)

        logger.info(f"Image médicale créée par {current_user.email}: {medical_image.file_name}")

        return MedicalImageResponse.model_validate(medical_image)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erreur lors de la création de l'image médicale: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de l'image médicale: {str(e)}"
        )

@router.get("/{image_id}", response_model=MedicalImageResponse)
async def get_medical_image(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère une image médicale par son ID"""
    try:
        result = await db.execute(
            select(MedicalImage).where(MedicalImage.id == image_id)
        )
        medical_image = result.scalar_one_or_none()

        if not medical_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image médicale non trouvée"
            )

        return MedicalImageResponse.model_validate(medical_image)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'image médicale: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/upload-modalities")
async def upload_medical_modalities(
    patient_id: str = Form(..., description="ID du patient"),
    t1_file: Optional[UploadFile] = File(None, description="Image T1 (.nii ou .nii.gz)"),
    t1ce_file: Optional[UploadFile] = File(None, description="Image T1CE (.nii ou .nii.gz)"),
    t2_file: Optional[UploadFile] = File(None, description="Image T2 (.nii ou .nii.gz)"),
    flair_file: Optional[UploadFile] = File(None, description="Image FLAIR (.nii ou .nii.gz)"),
    acquisition_date: Optional[str] = Form(None, description="Date d'acquisition (YYYY-MM-DD)"),
    notes: Optional[str] = Form(None, description="Notes additionnelles"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    🧠 Upload des 4 modalités d'images médicales pour segmentation de tumeurs cérébrales

    Modalités supportées :
    - **T1** : Anatomie de base
    - **T1CE** : T1 avec contraste (gadolinium)
    - **T2** : Détection d'œdème
    - **FLAIR** : Suppression du signal du liquide céphalo-rachidien

    Formats acceptés : .nii, .nii.gz
    """
    try:
        # Vérification des permissions
        if current_user.role.value not in ["ADMIN", "DOCTOR", "SECRETARY"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes pour uploader des images médicales"
            )

        # Vérifier qu'au moins une modalité est fournie
        uploaded_files = {
            "T1": t1_file,
            "T1CE": t1ce_file,
            "T2": t2_file,
            "FLAIR": flair_file
        }

        valid_files = {k: v for k, v in uploaded_files.items() if v is not None}

        if not valid_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Au moins une modalité d'image doit être fournie"
            )

        # Créer le dossier de destination avec gestion Windows
        upload_dir = Path("uploads") / "medical_images" / patient_id
        try:
            upload_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Dossier créé: {upload_dir}")
        except Exception as e:
            logger.error(f"Erreur création dossier {upload_dir}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Impossible de créer le dossier de destination: {str(e)}"
            )

        # Générer un ID unique pour cette série d'images
        series_id = str(uuid.uuid4())
        uploaded_images = []

        # Traiter chaque fichier
        for modality, file in valid_files.items():
            # Vérifier l'extension du fichier
            if not file.filename.lower().endswith(('.nii', '.nii.gz')):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Format de fichier non supporté pour {modality}. Utilisez .nii ou .nii.gz"
                )

            # Générer un nom de fichier unique
            file_extension = ".nii.gz" if file.filename.lower().endswith('.nii.gz') else ".nii"
            safe_filename = f"{series_id}_{modality.lower()}{file_extension}"
            file_path = upload_dir / safe_filename

            # Sauvegarder le fichier avec gestion d'erreur
            try:
                content = await file.read()
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(content)
                logger.info(f"Fichier sauvegardé: {file_path} ({len(content)} bytes)")
            except Exception as e:
                logger.error(f"Erreur sauvegarde fichier {file_path}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erreur lors de la sauvegarde du fichier {modality}: {str(e)}"
                )

            # Créer l'entrée en base de données
            medical_image = MedicalImage(
                id=str(uuid.uuid4()),
                patient_id=patient_id,
                uploaded_by_user_id=current_user.id,
                modality=modality,
                file_path=str(file_path),
                file_name=safe_filename,
                file_size=len(content),
                image_metadata={
                    "series_id": series_id,
                    "original_filename": file.filename,
                    "content_type": file.content_type
                },
                acquisition_date=datetime.strptime(acquisition_date, "%Y-%m-%d").date() if acquisition_date else None,
                body_part="BRAIN",
                notes=notes,
                is_processed=False,
                uploaded_at=datetime.now()
            )

            db.add(medical_image)
            uploaded_images.append({
                "modality": modality,
                "filename": safe_filename,
                "size_mb": round(len(content) / (1024 * 1024), 2),
                "path": str(file_path)
            })

        await db.commit()

        logger.info(f"Images médicales uploadées par {current_user.email} pour patient {patient_id}: {list(valid_files.keys())}")

        return {
            "success": True,
            "message": f"✅ {len(uploaded_images)} modalité(s) uploadée(s) avec succès",
            "series_id": series_id,
            "patient_id": patient_id,
            "uploaded_modalities": uploaded_images,
            "total_size_mb": round(sum(img["size_mb"] for img in uploaded_images), 2),
            "ready_for_segmentation": len(uploaded_images) >= 2  # Au moins 2 modalités pour la segmentation
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erreur lors de l'upload des images médicales: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )

@router.get("/patient/{patient_id}/modalities")
async def get_patient_modalities(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    📋 Récupère toutes les modalités d'images pour un patient donné

    Retourne les images groupées par série avec informations détaillées
    """
    try:
        # Récupérer toutes les images du patient
        result = await db.execute(
            select(MedicalImage).where(MedicalImage.patient_id == patient_id)
        )
        images = result.scalars().all()

        if not images:
            return {
                "patient_id": patient_id,
                "total_images": 0,
                "series": [],
                "available_modalities": [],
                "message": "Aucune image trouvée pour ce patient"
            }

        # Grouper par série
        series_dict = {}
        for image in images:
            series_id = image.image_metadata.get("series_id", "unknown") if image.image_metadata else "unknown"

            if series_id not in series_dict:
                series_dict[series_id] = {
                    "series_id": series_id,
                    "acquisition_date": image.acquisition_date,
                    "uploaded_at": image.uploaded_at,
                    "modalities": [],
                    "total_size_mb": 0,
                    "notes": image.notes
                }

            series_dict[series_id]["modalities"].append({
                "modality": image.modality,
                "filename": image.file_name,
                "size_mb": round(image.file_size / (1024 * 1024), 2) if image.file_size else 0,
                "is_processed": image.is_processed,
                "image_id": image.id
            })

            series_dict[series_id]["total_size_mb"] += round(image.file_size / (1024 * 1024), 2) if image.file_size else 0

        # Convertir en liste et trier
        series_list = list(series_dict.values())
        series_list.sort(key=lambda x: x["uploaded_at"], reverse=True)

        # Calculer les modalités disponibles
        all_modalities = set()
        for image in images:
            all_modalities.add(image.modality)

        return {
            "patient_id": patient_id,
            "total_images": len(images),
            "total_series": len(series_list),
            "series": series_list,
            "available_modalities": sorted(list(all_modalities)),
            "ready_for_segmentation": len(all_modalities) >= 2
        }

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modalités du patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.get("/debug/all-images")
async def debug_all_images(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    🔍 Debug - Liste toutes les images en base avec leurs patient_id
    """
    try:
        result = await db.execute(select(MedicalImage))
        images = result.scalars().all()

        debug_info = []
        for img in images:
            debug_info.append({
                "image_id": img.id,
                "patient_id": img.patient_id,
                "modality": img.modality,
                "filename": img.file_name,
                "uploaded_at": img.uploaded_at.isoformat() if img.uploaded_at else None,
                "series_id": img.image_metadata.get("series_id") if img.image_metadata else None
            })

        return {
            "total_images": len(images),
            "images": debug_info
        }

    except Exception as e:
        logger.error(f"Erreur debug: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur debug: {str(e)}"
        )

@router.get("/debug/patient/{patient_id}")
async def debug_patient_images(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    🔍 Debug - Vérification détaillée des images d'un patient
    """
    try:
        # Vérifier si le patient existe
        from models.database_models import Patient

        patient_result = await db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        patient = patient_result.scalar_one_or_none()

        # Récupérer les images
        images_result = await db.execute(
            select(MedicalImage).where(MedicalImage.patient_id == patient_id)
        )
        images = images_result.scalars().all()

        return {
            "patient_exists": patient is not None,
            "patient_info": {
                "id": patient.id if patient else None,
                "name": f"{patient.first_name} {patient.last_name}" if patient else None
            } if patient else None,
            "search_patient_id": patient_id,
            "images_found": len(images),
            "images_details": [
                {
                    "image_id": img.id,
                    "patient_id": img.patient_id,
                    "modality": img.modality,
                    "filename": img.file_name,
                    "uploaded_at": img.uploaded_at.isoformat() if img.uploaded_at else None
                }
                for img in images
            ]
        }

    except Exception as e:
        logger.error(f"Erreur debug patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur debug: {str(e)}"
        )

@router.post("/fix/create-missing-patient/{patient_id}")
async def fix_create_missing_patient(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    🛠️ Fix - Crée un patient manquant pour les images orphelines
    """
    try:
        from models.database_models import Patient, Gender
        from datetime import date

        # Vérifier si le patient existe déjà
        patient_result = await db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        existing_patient = patient_result.scalar_one_or_none()

        if existing_patient:
            return {
                "success": False,
                "message": "Patient existe déjà",
                "patient_id": patient_id
            }

        # Créer le patient manquant
        new_patient = Patient(
            id=patient_id,
            first_name="Patient",
            last_name="Test",
            date_of_birth=date(1980, 1, 1),
            gender=Gender.MALE,
            email="patient.test@cerebloom.com",
            phone="+33123456789",
            address="Adresse de test",
            created_by_user_id=current_user.id,
            notes="Patient créé automatiquement pour corriger les images orphelines"
        )

        db.add(new_patient)
        await db.commit()
        await db.refresh(new_patient)

        # Vérifier les images maintenant liées
        images_result = await db.execute(
            select(MedicalImage).where(MedicalImage.patient_id == patient_id)
        )
        images = images_result.scalars().all()

        return {
            "success": True,
            "message": "✅ Patient créé avec succès !",
            "patient_id": patient_id,
            "patient_name": f"{new_patient.first_name} {new_patient.last_name}",
            "images_now_linked": len(images),
            "modalities_available": [img.modality for img in images]
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Erreur création patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )

@router.delete("/series/{series_id}")
async def delete_image_series(
    series_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    🗑️ Supprime une série complète d'images médicales

    Supprime toutes les modalités d'une série et les fichiers associés
    """
    try:
        # Vérification des permissions
        if current_user.role.value not in ["ADMIN", "DOCTOR", "SECRETARY"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes pour supprimer des images médicales"
            )

        # Récupérer toutes les images de la série
        result = await db.execute(
            select(MedicalImage).where(
                MedicalImage.image_metadata.op('->>')('series_id') == series_id
            )
        )
        images = result.scalars().all()

        if not images:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Série d'images non trouvée"
            )

        deleted_files = []
        deleted_modalities = []

        # Supprimer les fichiers physiques et les entrées en base
        for image in images:
            try:
                # Supprimer le fichier physique
                file_path = Path(image.file_path)
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Fichier supprimé: {file_path}")
                    deleted_files.append(str(file_path))

                deleted_modalities.append({
                    "modality": image.modality,
                    "filename": image.file_name,
                    "size_mb": round(image.file_size / (1024 * 1024), 2) if image.file_size else 0
                })

                # Supprimer l'entrée en base
                await db.delete(image)

            except Exception as e:
                logger.error(f"Erreur suppression fichier {image.file_path}: {e}")
                # Continuer même si un fichier ne peut pas être supprimé

        await db.commit()

        logger.info(f"Série d'images supprimée par {current_user.email}: {series_id} ({len(deleted_modalities)} modalités)")

        return {
            "success": True,
            "message": f"✅ Série supprimée avec succès",
            "series_id": series_id,
            "deleted_modalities": deleted_modalities,
            "deleted_files": len(deleted_files),
            "total_deleted": len(deleted_modalities)
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erreur lors de la suppression de la série: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )