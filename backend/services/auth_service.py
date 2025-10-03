"""
🧠 CereBloom - Service d'Authentification
Gestion de l'authentification, des tokens JWT et des permissions
"""

import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
import logging

from config.settings import settings
from config.database import get_database
from models.database_models import User, UserCredentials, UserPermissions, UserSession
from models.api_models import UserResponse

logger = logging.getLogger(__name__)

class AuthService:
    """Service d'authentification et de gestion des utilisateurs"""

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def hash_password(self, password: str) -> Tuple[str, str]:
        """
        Hache un mot de passe avec un salt
        Returns: (password_hash, salt)
        """
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8'), salt.decode('utf-8')

    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Vérifie un mot de passe"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du mot de passe: {e}")
            return False

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Crée un token d'accès JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Crée un token de rafraîchissement JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expiré")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Token invalide: {e}")
            return None

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur"""
        async for db in get_database():
            try:
                # Recherche de l'utilisateur par username
                result = await db.execute(
                    select(User, UserCredentials)
                    .join(UserCredentials)
                    .where(UserCredentials.username == username)
                )
                user_data = result.first()

                if not user_data:
                    logger.warning(f"Utilisateur non trouvé: {username}")
                    return None

                user, credentials = user_data

                # Vérification du statut utilisateur
                if user.status != "ACTIVE":
                    logger.warning(f"Utilisateur inactif: {username}")
                    return None

                # Vérification du verrouillage
                if credentials.is_locked:
                    if credentials.locked_until and credentials.locked_until > datetime.utcnow():
                        logger.warning(f"Compte verrouillé: {username}")
                        return None
                    else:
                        # Déverrouillage automatique
                        credentials.is_locked = False
                        credentials.locked_until = None
                        credentials.failed_login_attempts = 0
                        await db.commit()

                # Vérification du mot de passe
                if self.verify_password(password, credentials.password_hash, credentials.salt):
                    # Réinitialisation des tentatives échouées
                    credentials.failed_login_attempts = 0
                    credentials.last_login = datetime.utcnow()
                    await db.commit()

                    logger.info(f"Authentification réussie: {username}")
                    return user
                else:
                    # Incrémentation des tentatives échouées
                    credentials.failed_login_attempts += 1

                    # Verrouillage après 5 tentatives
                    if credentials.failed_login_attempts >= 5:
                        credentials.is_locked = True
                        credentials.locked_until = datetime.utcnow() + timedelta(minutes=30)
                        logger.warning(f"Compte verrouillé après 5 tentatives: {username}")

                    await db.commit()
                    logger.warning(f"Mot de passe incorrect: {username}")
                    return None

            except Exception as e:
                logger.error(f"Erreur lors de l'authentification: {e}")
                await db.rollback()
                return None

    async def authenticate_user_by_email(self, email: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur par email"""
        async for db in get_database():
            try:
                # Recherche de l'utilisateur par email
                result = await db.execute(
                    select(User, UserCredentials)
                    .join(UserCredentials)
                    .where(User.email == email)
                )
                user_data = result.first()

                if not user_data:
                    logger.warning(f"Utilisateur non trouvé: {email}")
                    return None

                user, credentials = user_data

                # Vérification du statut utilisateur
                if user.status != "ACTIVE":
                    logger.warning(f"Utilisateur inactif: {email}")
                    return None

                # Vérification du verrouillage
                if credentials.is_locked:
                    if credentials.locked_until and credentials.locked_until > datetime.utcnow():
                        logger.warning(f"Compte verrouillé: {email}")
                        return None
                    else:
                        # Déverrouillage automatique
                        credentials.is_locked = False
                        credentials.locked_until = None
                        credentials.failed_login_attempts = 0
                        await db.commit()

                # Vérification du mot de passe
                if self.verify_password(password, credentials.password_hash, credentials.salt):
                    # Réinitialisation des tentatives échouées
                    credentials.failed_login_attempts = 0
                    credentials.last_login = datetime.utcnow()
                    await db.commit()

                    logger.info(f"Authentification réussie: {email}")
                    return user
                else:
                    # Incrémentation des tentatives échouées
                    credentials.failed_login_attempts += 1

                    # Verrouillage après 5 tentatives
                    if credentials.failed_login_attempts >= 5:
                        credentials.is_locked = True
                        credentials.locked_until = datetime.utcnow() + timedelta(minutes=30)
                        logger.warning(f"Compte verrouillé après 5 tentatives: {email}")

                    await db.commit()
                    logger.warning(f"Mot de passe incorrect: {email}")
                    return None

            except Exception as e:
                logger.error(f"Erreur lors de l'authentification par email: {e}")
                await db.rollback()
                return None

    async def get_current_user(self, token: str) -> Optional[User]:
        """Récupère l'utilisateur actuel à partir du token"""
        payload = self.verify_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        async for db in get_database():
            try:
                result = await db.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()

                if user and user.status == "ACTIVE":
                    return user
                return None

            except Exception as e:
                logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
                return None

    async def create_user_session(self, user: User, ip_address: str, user_agent: str) -> str:
        """Crée une session utilisateur"""
        async for db in get_database():
            try:
                session_id = secrets.token_urlsafe(32)
                expires_at = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

                session = UserSession(
                    session_id=session_id,
                    user_id=user.id,
                    expires_at=expires_at,
                    ip_address=ip_address,
                    user_agent=user_agent
                )

                db.add(session)
                await db.commit()

                return session_id

            except Exception as e:
                logger.error(f"Erreur lors de la création de session: {e}")
                await db.rollback()
                raise

    async def invalidate_user_sessions(self, user_id: str) -> None:
        """Invalide toutes les sessions d'un utilisateur"""
        async for db in get_database():
            try:
                result = await db.execute(
                    select(UserSession).where(UserSession.user_id == user_id)
                )
                sessions = result.scalars().all()

                for session in sessions:
                    session.is_active = False

                await db.commit()
                logger.info(f"Sessions invalidées pour l'utilisateur: {user_id}")

            except Exception as e:
                logger.error(f"Erreur lors de l'invalidation des sessions: {e}")
                await db.rollback()

    async def check_permission(self, user: User, permission: str) -> bool:
        """Vérifie si un utilisateur a une permission spécifique"""
        async for db in get_database():
            try:
                result = await db.execute(
                    select(UserPermissions).where(UserPermissions.user_id == user.id)
                )
                permissions = result.scalar_one_or_none()

                if not permissions:
                    return False

                # Vérification de la permission
                return getattr(permissions, permission, False)

            except Exception as e:
                logger.error(f"Erreur lors de la vérification des permissions: {e}")
                return False

    async def generate_password_reset_token(self, email: str) -> Optional[str]:
        """Génère un token de réinitialisation de mot de passe"""
        async for db in get_database():
            try:
                result = await db.execute(
                    select(User, UserCredentials)
                    .join(UserCredentials)
                    .where(User.email == email)
                )
                user_data = result.first()

                if not user_data:
                    return None

                user, credentials = user_data

                # Génération du token
                reset_token = secrets.token_urlsafe(32)
                credentials.reset_token = reset_token
                credentials.token_expires_at = datetime.utcnow() + timedelta(hours=1)

                await db.commit()

                logger.info(f"Token de réinitialisation généré pour: {email}")
                return reset_token

            except Exception as e:
                logger.error(f"Erreur lors de la génération du token de réinitialisation: {e}")
                await db.rollback()
                return None

    async def reset_password_with_token(self, token: str, new_password: str) -> bool:
        """Réinitialise un mot de passe avec un token"""
        async for db in get_database():
            try:
                result = await db.execute(
                    select(UserCredentials)
                    .where(
                        UserCredentials.reset_token == token,
                        UserCredentials.token_expires_at > datetime.utcnow()
                    )
                )
                credentials = result.scalar_one_or_none()

                if not credentials:
                    return False

                # Mise à jour du mot de passe
                password_hash, salt = self.hash_password(new_password)
                credentials.password_hash = password_hash
                credentials.salt = salt
                credentials.reset_token = None
                credentials.token_expires_at = None
                credentials.failed_login_attempts = 0
                credentials.is_locked = False
                credentials.locked_until = None

                await db.commit()

                logger.info(f"Mot de passe réinitialisé pour l'utilisateur: {credentials.user_id}")
                return True

            except Exception as e:
                logger.error(f"Erreur lors de la réinitialisation du mot de passe: {e}")
                await db.rollback()
                return False


# Configuration pour FastAPI Depends
from fastapi.security import HTTPBearer
security = HTTPBearer()

# Fonction wrapper pour FastAPI Depends
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Fonction wrapper pour utiliser AuthService.get_current_user comme dépendance FastAPI
    """

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'authentification requis"
        )

    auth_service = AuthService()
    user = await auth_service.get_current_user(credentials.credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )

    return user
