"""
🧠 CereBloom - Router Rapports
Endpoints pour la gestion des rapports
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging

from config.database import get_database
from services.auth_service import AuthService
from models.api_models import BaseResponse, SegmentationReportCreate, SegmentationReportResponse
from models.database_models import User, SegmentationReport

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
async def get_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère la liste des rapports avec les données liées"""
    try:
        from models.database_models import Doctor, User, AISegmentation, Patient
        from sqlalchemy.orm import selectinload

        # Récupérer les rapports avec les données liées
        result = await db.execute(
            select(SegmentationReport)
            .options(
                selectinload(SegmentationReport.doctor).selectinload(Doctor.user),
                selectinload(SegmentationReport.segmentation).selectinload(AISegmentation.patient)
            )
        )
        reports = result.scalars().all()

        # Construire la réponse avec les données liées
        reports_data = []
        for report in reports:
            report_dict = SegmentationReportResponse.model_validate(report).model_dump()

            # Ajouter les données du médecin
            if report.doctor and report.doctor.user:
                report_dict["doctor"] = {
                    "id": report.doctor.id,
                    "user": {
                        "first_name": report.doctor.user.first_name,
                        "last_name": report.doctor.user.last_name,
                        "email": report.doctor.user.email
                    }
                }

            # Ajouter les données de la segmentation et du patient
            if report.segmentation:
                report_dict["segmentation"] = {
                    "id": report.segmentation.id,
                    "patient_id": report.segmentation.patient_id,
                    "status": report.segmentation.status
                }

                if report.segmentation.patient:
                    report_dict["segmentation"]["patient"] = {
                        "first_name": report.segmentation.patient.first_name,
                        "last_name": report.segmentation.patient.last_name,
                        "email": report.segmentation.patient.email
                    }

            reports_data.append(report_dict)

        return {"reports": reports_data}

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des rapports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/", response_model=SegmentationReportResponse)
async def create_segmentation_report(
    report_data: SegmentationReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Crée un nouveau rapport de segmentation"""
    try:
        import uuid
        from datetime import datetime

        # Vérification des permissions (Docteur ou Admin)
        if current_user.role.value not in ["ADMIN", "DOCTOR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes pour créer un rapport"
            )

        # Récupérer le profil médecin de l'utilisateur connecté
        doctor_id = report_data.doctor_id

        if not doctor_id:
            # Si pas de doctor_id spécifié, utiliser celui de l'utilisateur connecté
            if current_user.role.value == "DOCTOR":
                from models.database_models import Doctor
                doctor_result = await db.execute(
                    select(Doctor).where(Doctor.user_id == current_user.id)
                )
                doctor_profile = doctor_result.scalar_one_or_none()

                if not doctor_profile:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Profil médecin non trouvé pour cet utilisateur"
                    )
                doctor_id = doctor_profile.id
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="doctor_id requis pour les utilisateurs non-médecins"
                )

        # Création du rapport
        report = SegmentationReport(
            id=str(uuid.uuid4()),
            segmentation_id=report_data.segmentation_id,
            doctor_id=doctor_id,
            report_content=report_data.report_content,
            findings=report_data.findings,
            recommendations=report_data.recommendations,
            image_attachments=report_data.image_attachments,
            template_used=report_data.template_used,
            quantitative_metrics=report_data.quantitative_metrics,
            is_final=report_data.is_final if report_data.is_final is not None else False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(report)
        await db.commit()
        await db.refresh(report)

        logger.info(f"Rapport créé par {current_user.email}: {report.id}")

        return SegmentationReportResponse.model_validate(report)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erreur lors de la création du rapport: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du rapport: {str(e)}"
        )

@router.get("/{report_id}", response_model=SegmentationReportResponse)
async def get_segmentation_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Récupère un rapport par son ID avec les données liées"""
    try:
        from models.database_models import Doctor, User, AISegmentation, Patient
        from sqlalchemy.orm import selectinload

        # Récupérer le rapport avec les données liées
        result = await db.execute(
            select(SegmentationReport)
            .where(SegmentationReport.id == report_id)
            .options(
                selectinload(SegmentationReport.doctor).selectinload(Doctor.user),
                selectinload(SegmentationReport.segmentation).selectinload(AISegmentation.patient)
            )
        )
        report = result.scalar_one_or_none()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rapport non trouvé"
            )

        # Construire la réponse avec les données liées
        report_dict = SegmentationReportResponse.model_validate(report).model_dump()

        # Ajouter les données du médecin
        if report.doctor and report.doctor.user:
            report_dict["doctor"] = {
                "id": report.doctor.id,
                "user": {
                    "first_name": report.doctor.user.first_name,
                    "last_name": report.doctor.user.last_name,
                    "email": report.doctor.user.email
                }
            }

        # Ajouter les données de la segmentation et du patient
        if report.segmentation:
            report_dict["segmentation"] = {
                "id": report.segmentation.id,
                "patient_id": report.segmentation.patient_id,
                "status": report.segmentation.status
            }

            if report.segmentation.patient:
                report_dict["segmentation"]["patient"] = {
                    "first_name": report.segmentation.patient.first_name,
                    "last_name": report.segmentation.patient.last_name,
                    "email": report.segmentation.patient.email
                }

        return report_dict

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du rapport: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.put("/{report_id}", response_model=SegmentationReportResponse)
async def update_segmentation_report(
    report_id: str,
    report_data: SegmentationReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Met à jour un rapport de segmentation"""
    try:
        from datetime import datetime

        # Vérification des permissions (Docteur ou Admin)
        if current_user.role.value not in ["ADMIN", "DOCTOR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes pour modifier un rapport"
            )

        # Récupérer le rapport existant
        result = await db.execute(
            select(SegmentationReport).where(SegmentationReport.id == report_id)
        )
        report = result.scalar_one_or_none()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rapport non trouvé"
            )

        # Mettre à jour les champs
        if report_data.report_content is not None:
            report.report_content = report_data.report_content
        if report_data.findings is not None:
            report.findings = report_data.findings
        if report_data.recommendations is not None:
            report.recommendations = report_data.recommendations
        if report_data.image_attachments is not None:
            report.image_attachments = report_data.image_attachments
        if report_data.template_used is not None:
            report.template_used = report_data.template_used
        if report_data.quantitative_metrics is not None:
            report.quantitative_metrics = report_data.quantitative_metrics
        if report_data.is_final is not None:
            report.is_final = report_data.is_final

        report.updated_at = datetime.now()

        await db.commit()
        await db.refresh(report)

        logger.info(f"Rapport mis à jour par {current_user.email}: {report.id}")

        return SegmentationReportResponse.model_validate(report)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erreur lors de la mise à jour du rapport: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour du rapport: {str(e)}"
        )

@router.get("/{report_id}/download")
async def download_segmentation_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Télécharge un rapport en format PDF"""
    try:
        from fastapi.responses import Response
        from models.database_models import Doctor, AISegmentation
        from sqlalchemy.orm import selectinload
        from datetime import datetime

        # Vérifier les permissions
        if current_user.role.value not in ["ADMIN", "DOCTOR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes pour télécharger un rapport"
            )

        # Récupérer le rapport avec les données liées
        result = await db.execute(
            select(SegmentationReport)
            .where(SegmentationReport.id == report_id)
            .options(
                selectinload(SegmentationReport.doctor).selectinload(Doctor.user),
                selectinload(SegmentationReport.segmentation).selectinload(AISegmentation.patient)
            )
        )
        report = result.scalar_one_or_none()

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rapport non trouvé"
            )

        # Vérifier que le rapport est final
        if not report.is_final:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seuls les rapports finaux peuvent être téléchargés"
            )

        # Générer le contenu du rapport en format texte (pour l'instant)
        # TODO: Implémenter la génération PDF avec reportlab ou weasyprint

        patient_name = "Patient non spécifié"
        doctor_name = "Médecin non spécifié"

        if report.segmentation and report.segmentation.patient:
            patient_name = f"{report.segmentation.patient.first_name} {report.segmentation.patient.last_name}"

        if report.doctor and report.doctor.user:
            doctor_name = f"Dr. {report.doctor.user.first_name} {report.doctor.user.last_name}"

        report_content = f"""
RAPPORT DE SEGMENTATION IA
========================

Rapport ID: {report.id}
Date de création: {report.created_at.strftime('%d/%m/%Y %H:%M')}
Statut: {'Final' if report.is_final else 'Brouillon'}

INFORMATIONS PATIENT
===================
Patient: {patient_name}
Médecin: {doctor_name}

SEGMENTATION
============
ID Segmentation: {report.segmentation_id}
Statut: {report.segmentation.status if report.segmentation else 'N/A'}

CONTENU DU RAPPORT
==================
{report.report_content}

---
Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}
CereBloom - Système de Segmentation IA
        """.strip()

        # Retourner le fichier en tant que téléchargement
        filename = f"rapport_segmentation_{report.id[:8]}_{datetime.now().strftime('%Y%m%d')}.txt"

        return Response(
            content=report_content.encode('utf-8'),
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement du rapport: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du téléchargement"
        )
