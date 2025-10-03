"""
🧠 CereBloom - Configuration Base de Données
Configuration SQLAlchemy avec support async
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
import logging
from typing import AsyncGenerator
from config.settings import settings

logger = logging.getLogger(__name__)

# Base pour les modèles SQLAlchemy
class Base(DeclarativeBase):
    """Classe de base pour tous les modèles SQLAlchemy"""
    pass

# Moteur de base de données async
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Session maker async
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False
)

# Moteur synchrone pour les migrations
sync_engine = create_engine(
    settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://"),
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Session maker synchrone
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """
    Générateur de session de base de données async
    Utilisé comme dépendance FastAPI
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Erreur de base de données: {e}")
            raise
        finally:
            await session.close()

async def init_database():
    """Initialise la base de données et crée les tables"""
    try:
        # Import des modèles pour s'assurer qu'ils sont enregistrés
        import models.database_models

        # Création des tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ Base de données initialisée avec succès")

        # Création des données de base si nécessaire
        await create_initial_data()

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
        raise

async def create_initial_data():
    """Crée les données initiales nécessaires"""
    try:
        from models.database_models import User, UserCredentials, UserPermissions
        from services.auth_service import AuthService
        from config.settings import USER_ROLE_PERMISSIONS
        import uuid

        async with AsyncSessionLocal() as session:

            # Vérifier si l'admin existe déjà
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.email == "admin@cerebloom.com")
            )
            admin_user = result.scalar_one_or_none()

            if not admin_user:
                # Créer l'utilisateur admin par défaut
                auth_service = AuthService()

                admin_id = str(uuid.uuid4())
                admin_user = User(
                    id=admin_id,
                    first_name="Admin",
                    last_name="CereBloom",
                    email="admin@cerebloom.com",
                    phone="+1-234-567-8900",
                    role="ADMIN",
                    status="ACTIVE",
                    employee_id="ADMIN001"
                )

                # Credentials
                password_hash, salt = auth_service.hash_password("admin123")
                admin_credentials = UserCredentials(
                    user_id=admin_id,
                    username="admin",
                    password_hash=password_hash,
                    salt=salt
                )

                # Permissions
                admin_permissions = UserPermissions(
                    user_id=admin_id,
                    **USER_ROLE_PERMISSIONS["ADMIN"]
                )

                session.add(admin_user)
                session.add(admin_credentials)
                session.add(admin_permissions)

                await session.commit()
                logger.info("✅ Utilisateur admin créé: admin@cerebloom.com / admin123")

            # Créer des templates de rapports par défaut
            await create_default_report_templates(session, admin_user.id)

    except Exception as e:
        logger.error(f"❌ Erreur lors de la création des données initiales: {e}")
        raise

async def create_default_report_templates(session: AsyncSession, admin_user_id: str):
    """Crée les templates de rapports par défaut"""
    try:
        from models.database_models import ReportTemplate
        from sqlalchemy import select
        import uuid

        # Template de rapport de segmentation
        result = await session.execute(
            select(ReportTemplate).where(ReportTemplate.template_name == "Rapport de Segmentation Standard")
        )
        if not result.scalar_one_or_none():
            segmentation_template = ReportTemplate(
                id=str(uuid.uuid4()),
                template_name="Rapport de Segmentation Standard",
                template_type="SEGMENTATION",
                content_template="""
# Rapport de Segmentation - {patient_name}

## Informations Patient
- **Nom**: {patient_name}
- **Date de naissance**: {patient_dob}
- **Date d'examen**: {exam_date}

## Résultats de Segmentation
- **Volume tumoral total**: {total_volume} cm³
- **Noyau nécrotique**: {necrotic_volume} cm³ ({necrotic_percentage}%)
- **Œdème péritumoral**: {edema_volume} cm³ ({edema_percentage}%)
- **Tumeur rehaussée**: {enhancing_volume} cm³ ({enhancing_percentage}%)

## Score de Confiance
- **Score global**: {confidence_score}

## Recommandations
{recommendations}

## Images
{segmentation_images}
                """,
                fields_mapping={
                    "patient_name": "patient.first_name + ' ' + patient.last_name",
                    "patient_dob": "patient.date_of_birth",
                    "exam_date": "segmentation.completed_at",
                    "total_volume": "volumetric_analysis.total_tumor_volume",
                    "necrotic_volume": "volumetric_analysis.necrotic_core_volume",
                    "edema_volume": "volumetric_analysis.peritumoral_edema_volume",
                    "enhancing_volume": "volumetric_analysis.enhancing_tumor_volume",
                    "confidence_score": "segmentation.confidence_score"
                },
                category="MEDICAL",
                is_active=True,
                created_by_user_id=admin_user_id
            )
            session.add(segmentation_template)

        # Template de rapport de consultation
        result = await session.execute(
            select(ReportTemplate).where(ReportTemplate.template_name == "Rapport de Consultation Standard")
        )
        if not result.scalar_one_or_none():
            consultation_template = ReportTemplate(
                id=str(uuid.uuid4()),
                template_name="Rapport de Consultation Standard",
                template_type="CONSULTATION",
                content_template="""
# Rapport de Consultation - {patient_name}

## Informations Patient
- **Nom**: {patient_name}
- **Date de consultation**: {consultation_date}
- **Médecin**: {doctor_name}

## Motif de consultation
{chief_complaint}

## Symptômes
{symptoms}

## Examen physique
{physical_examination}

## Diagnostic
{diagnosis}

## Notes
{notes}

## Plan de traitement
{treatment_plan}
                """,
                fields_mapping={
                    "patient_name": "patient.first_name + ' ' + patient.last_name",
                    "consultation_date": "medical_record.consultation_date",
                    "doctor_name": "doctor.user.first_name + ' ' + doctor.user.last_name",
                    "chief_complaint": "medical_record.chief_complaint",
                    "symptoms": "medical_record.symptoms",
                    "physical_examination": "medical_record.physical_examination",
                    "diagnosis": "medical_record.diagnosis",
                    "notes": "medical_record.notes"
                },
                category="MEDICAL",
                is_active=True,
                created_by_user_id=admin_user_id
            )
            session.add(consultation_template)

        await session.commit()
        logger.info("✅ Templates de rapports par défaut créés")

    except Exception as e:
        logger.error(f"❌ Erreur lors de la création des templates: {e}")


async def reset_database():
    """Remet à zéro la base de données (ATTENTION: supprime toutes les données)"""
    try:
        import models.database_models

        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ Base de données remise à zéro")
        await create_initial_data()

    except Exception as e:
        logger.error(f"❌ Erreur lors de la remise à zéro: {e}")
        raise

# Utilitaires pour les tests
async def get_test_session() -> AsyncSession:
    """Retourne une session de test"""
    return AsyncSessionLocal()

def get_sync_session():
    """Retourne une session synchrone pour les migrations"""
    return SessionLocal()

# Health check de la base de données
async def check_database_health() -> bool:
    """Vérifie la santé de la base de données"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"❌ Base de données non disponible: {e}")
        return False
