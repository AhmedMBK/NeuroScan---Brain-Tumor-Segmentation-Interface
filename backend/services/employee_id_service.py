"""
🏷️ Service de génération automatique d'employee_id
Génère des identifiants métier uniques et lisibles pour CereBloom
"""

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from models.database_models import User, UserRole
from typing import Optional
import re


class EmployeeIdService:
    """Service de génération d'employee_id automatique"""

    # Préfixes par rôle
    ROLE_PREFIXES = {
        UserRole.DOCTOR: "DOC",
        UserRole.SECRETARY: "SEC",
        UserRole.ADMIN: "ADM"
    }

    @classmethod
    def generate_employee_id(cls, db: Session, role: UserRole, custom_prefix: Optional[str] = None) -> str:
        """
        Génère un employee_id unique automatiquement

        Args:
            db: Session de base de données
            role: Rôle de l'utilisateur
            custom_prefix: Préfixe personnalisé (optionnel)

        Returns:
            str: employee_id généré (ex: "DOC001", "SEC045")
        """
        # Déterminer le préfixe
        prefix = custom_prefix or cls.ROLE_PREFIXES.get(role, "USR")

        # Trouver le dernier numéro utilisé pour ce préfixe
        last_employee = db.query(User)\
            .filter(User.employee_id.like(f"{prefix}%"))\
            .order_by(User.employee_id.desc())\
            .first()

        if last_employee and last_employee.employee_id:
            # Extraire le numéro du dernier employee_id
            match = re.search(r'(\d+)$', last_employee.employee_id)
            if match:
                last_number = int(match.group(1))
                next_number = last_number + 1
            else:
                next_number = 1
        else:
            next_number = 1

        # Générer le nouvel employee_id
        new_employee_id = f"{prefix}{next_number:03d}"

        # Vérifier l'unicité (sécurité supplémentaire)
        while cls.employee_id_exists(db, new_employee_id):
            next_number += 1
            new_employee_id = f"{prefix}{next_number:03d}"

        return new_employee_id

    @classmethod
    def employee_id_exists(cls, db: Session, employee_id: str) -> bool:
        """Vérifie si un employee_id existe déjà"""
        return db.query(User).filter(User.employee_id == employee_id).first() is not None

    @classmethod
    def validate_employee_id_format(cls, employee_id: str) -> bool:
        """
        Valide le format d'un employee_id
        Format attendu: 3 lettres + 3 chiffres (ex: DOC001, SEC045)
        """
        pattern = r'^[A-Z]{3}\d{3}$'
        return bool(re.match(pattern, employee_id))

    @classmethod
    def get_next_available_id(cls, db: Session, prefix: str) -> str:
        """Obtient le prochain ID disponible pour un préfixe donné"""
        return cls.generate_employee_id(db, None, prefix)

    @classmethod
    def get_role_statistics(cls, db: Session) -> dict:
        """Obtient des statistiques sur les employee_id par rôle"""
        stats = {}

        for role, prefix in cls.ROLE_PREFIXES.items():
            count = db.query(func.count(User.id))\
                .filter(User.employee_id.like(f"{prefix}%"))\
                .scalar()

            last_id = db.query(User.employee_id)\
                .filter(User.employee_id.like(f"{prefix}%"))\
                .order_by(User.employee_id.desc())\
                .first()

            stats[role.value] = {
                "prefix": prefix,
                "count": count,
                "last_id": last_id[0] if last_id else None,
                "next_available": cls.generate_employee_id(db, role)
            }

        return stats

    @classmethod
    def suggest_employee_id(cls, db: Session, first_name: str, last_name: str, role: UserRole) -> str:
        """
        Suggère un employee_id basé sur le nom (optionnel)
        Fallback sur la génération automatique
        """
        # Tentative de génération basée sur les initiales
        initials = f"{first_name[0]}{last_name[0]}".upper()
        prefix = cls.ROLE_PREFIXES.get(role, "USR")

        # Essayer avec les initiales
        suggested_id = f"{prefix}{initials}1"
        if len(suggested_id) == 6 and not cls.employee_id_exists(db, suggested_id):
            return suggested_id

        # Fallback sur la génération automatique
        return cls.generate_employee_id(db, role)


# Fonctions utilitaires pour l'API
def auto_generate_employee_id(db: Session, role: UserRole) -> str:
    """Fonction simple pour générer un employee_id"""
    return EmployeeIdService.generate_employee_id(db, role)


def validate_or_generate_employee_id(
    db: Session,
    employee_id: Optional[str],
    role: UserRole
) -> str:
    """
    Valide un employee_id fourni ou en génère un automatiquement

    Args:
        db: Session de base de données
        employee_id: employee_id fourni (peut être None ou vide)
        role: Rôle de l'utilisateur

    Returns:
        str: employee_id validé ou généré
    """
    # Si aucun employee_id fourni, générer automatiquement
    if not employee_id or employee_id.strip() == "":
        return EmployeeIdService.generate_employee_id(db, role)

    # Nettoyer l'employee_id fourni
    employee_id = employee_id.strip().upper()

    # Valider le format
    if not EmployeeIdService.validate_employee_id_format(employee_id):
        raise ValueError(f"Format d'employee_id invalide: {employee_id}. Format attendu: XXX000 (ex: DOC001)")

    # Vérifier l'unicité
    if EmployeeIdService.employee_id_exists(db, employee_id):
        raise ValueError(f"L'employee_id {employee_id} existe déjà")

    return employee_id


# ===== VERSIONS ASYNC POUR FASTAPI =====

class AsyncEmployeeIdService:
    """Version async du service pour FastAPI"""

    ROLE_PREFIXES = EmployeeIdService.ROLE_PREFIXES

    @classmethod
    async def generate_employee_id(cls, db: AsyncSession, role: UserRole, custom_prefix: Optional[str] = None) -> str:
        """Version async de la génération d'employee_id"""
        prefix = custom_prefix or cls.ROLE_PREFIXES.get(role, "USR")

        # Trouver le dernier numéro utilisé
        result = await db.execute(
            select(User.employee_id)
            .where(User.employee_id.like(f"{prefix}%"))
            .order_by(User.employee_id.desc())
        )
        last_employee_id = result.scalar()

        if last_employee_id:
            match = re.search(r'(\d+)$', last_employee_id)
            if match:
                last_number = int(match.group(1))
                next_number = last_number + 1
            else:
                next_number = 1
        else:
            next_number = 1

        # Générer le nouvel employee_id
        new_employee_id = f"{prefix}{next_number:03d}"

        # Vérifier l'unicité
        while await cls.employee_id_exists(db, new_employee_id):
            next_number += 1
            new_employee_id = f"{prefix}{next_number:03d}"

        return new_employee_id

    @classmethod
    async def employee_id_exists(cls, db: AsyncSession, employee_id: str) -> bool:
        """Version async de la vérification d'existence"""
        result = await db.execute(
            select(User.id).where(User.employee_id == employee_id)
        )
        return result.scalar() is not None

    @classmethod
    async def get_role_statistics(cls, db: AsyncSession) -> dict:
        """Version async des statistiques"""
        stats = {}

        for role, prefix in cls.ROLE_PREFIXES.items():
            # Compter les utilisateurs
            count_result = await db.execute(
                select(func.count(User.id)).where(User.employee_id.like(f"{prefix}%"))
            )
            count = count_result.scalar()

            # Dernier ID
            last_result = await db.execute(
                select(User.employee_id)
                .where(User.employee_id.like(f"{prefix}%"))
                .order_by(User.employee_id.desc())
            )
            last_id = last_result.scalar()

            # Prochain disponible
            next_available = await cls.generate_employee_id(db, role)

            stats[role.value] = {
                "prefix": prefix,
                "count": count,
                "last_id": last_id,
                "next_available": next_available
            }

        return stats


# Fonctions utilitaires async
async def async_auto_generate_employee_id(db: AsyncSession, role: UserRole) -> str:
    """Fonction async simple pour générer un employee_id"""
    return await AsyncEmployeeIdService.generate_employee_id(db, role)


async def async_validate_or_generate_employee_id(
    db: AsyncSession,
    employee_id: Optional[str],
    role: UserRole
) -> str:
    """Version async de la validation ou génération d'employee_id"""
    # Si aucun employee_id fourni, générer automatiquement
    if not employee_id or employee_id.strip() == "":
        return await AsyncEmployeeIdService.generate_employee_id(db, role)

    # Nettoyer l'employee_id fourni
    employee_id = employee_id.strip().upper()

    # Valider le format
    if not EmployeeIdService.validate_employee_id_format(employee_id):
        raise ValueError(f"Format d'employee_id invalide: {employee_id}. Format attendu: XXX000 (ex: DOC001)")

    # Vérifier l'unicité
    if await AsyncEmployeeIdService.employee_id_exists(db, employee_id):
        raise ValueError(f"L'employee_id {employee_id} existe déjà")

    return employee_id


# Exemples d'utilisation
"""
# SYNC (pour scripts/migrations)
employee_id = auto_generate_employee_id(db, UserRole.DOCTOR)

# ASYNC (pour FastAPI)
employee_id = await async_auto_generate_employee_id(db, UserRole.DOCTOR)
employee_id = await async_validate_or_generate_employee_id(db, "", UserRole.SECRETARY)
stats = await AsyncEmployeeIdService.get_role_statistics(db)
"""
