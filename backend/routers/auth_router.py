"""
🧠 CereBloom - Router d'Authentification
Endpoints pour l'authentification et la gestion des sessions
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging

from config.database import get_database
from services.auth_service import AuthService
from models.api_models import (
    LoginRequest, LoginResponse, TokenRefreshRequest,
    PasswordResetRequest, PasswordChangeRequest,
    UserResponse, BaseResponse, ErrorResponse
)
from models.database_models import User

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """
    Authentification utilisateur

    - **username**: Nom d'utilisateur
    - **password**: Mot de passe
    """
    try:
        auth_service = AuthService()

        # Authentification avec email
        user = await auth_service.authenticate_user_by_email(
            login_data.email,
            login_data.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants invalides"
            )

        # Création des tokens
        token_data = {"sub": user.id, "role": user.role.value}
        access_token = auth_service.create_access_token(token_data)
        refresh_token = auth_service.create_refresh_token(token_data)

        # Création de la session
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        session_id = await auth_service.create_user_session(
            user, client_ip, user_agent
        )

        logger.info(f"Connexion réussie: {user.email}")

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_service.access_token_expire_minutes * 60,
            user=UserResponse.from_orm(user)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/refresh", response_model=Dict[str, str])
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: AsyncSession = Depends(get_database)
):
    """
    Rafraîchissement du token d'accès

    - **refresh_token**: Token de rafraîchissement
    """
    try:
        auth_service = AuthService()

        # Vérification du refresh token
        payload = auth_service.verify_token(refresh_data.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de rafraîchissement invalide"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )

        # Vérification de l'utilisateur
        user = await auth_service.get_current_user(refresh_data.refresh_token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non trouvé"
            )

        # Création d'un nouveau token d'accès
        token_data = {"sub": user.id, "role": user.role.value}
        new_access_token = auth_service.create_access_token(token_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": auth_service.access_token_expire_minutes * 60
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du rafraîchissement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/logout", response_model=BaseResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_database)
):
    """
    Déconnexion utilisateur
    Invalide toutes les sessions de l'utilisateur
    """
    try:
        auth_service = AuthService()

        # Récupération de l'utilisateur actuel
        user = await auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )

        # Invalidation des sessions
        await auth_service.invalidate_user_sessions(user.id)

        logger.info(f"Déconnexion: {user.email}")

        return BaseResponse(message="Déconnexion réussie")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/password-reset-request", response_model=BaseResponse)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_database)
):
    """
    Demande de réinitialisation de mot de passe

    - **email**: Adresse email de l'utilisateur
    """
    try:
        auth_service = AuthService()

        # Génération du token de réinitialisation
        reset_token = await auth_service.generate_password_reset_token(reset_data.email)

        if reset_token:
            # TODO: Envoyer l'email avec le token
            # await send_password_reset_email(reset_data.email, reset_token)
            logger.info(f"Token de réinitialisation généré pour: {reset_data.email}")

        # Toujours retourner succès pour des raisons de sécurité
        return BaseResponse(
            message="Si l'adresse email existe, un lien de réinitialisation a été envoyé"
        )

    except Exception as e:
        logger.error(f"Erreur lors de la demande de réinitialisation: {e}")
        # Toujours retourner succès pour des raisons de sécurité
        return BaseResponse(
            message="Si l'adresse email existe, un lien de réinitialisation a été envoyé"
        )

@router.post("/password-reset", response_model=BaseResponse)
async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_database)
):
    """
    Réinitialisation du mot de passe avec token

    - **token**: Token de réinitialisation
    - **new_password**: Nouveau mot de passe
    """
    try:
        auth_service = AuthService()

        # Réinitialisation du mot de passe
        success = await auth_service.reset_password_with_token(token, new_password)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token invalide ou expiré"
            )

        logger.info("Mot de passe réinitialisé avec succès")

        return BaseResponse(message="Mot de passe réinitialisé avec succès")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/change-password", response_model=BaseResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_database)
):
    """
    Changement de mot de passe pour un utilisateur connecté

    - **current_password**: Mot de passe actuel
    - **new_password**: Nouveau mot de passe
    """
    try:
        auth_service = AuthService()

        # Récupération de l'utilisateur actuel
        user = await auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )

        # Récupération des credentials
        from sqlalchemy import select
        from models.database_models import UserCredentials

        result = await db.execute(
            select(UserCredentials).where(UserCredentials.user_id == user.id)
        )
        credentials = result.scalar_one_or_none()

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Credentials non trouvés"
            )

        # Vérification du mot de passe actuel
        current_user = await auth_service.authenticate_user(
            credentials.username,
            password_data.current_password
        )

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mot de passe actuel incorrect"
            )

        # Mise à jour du mot de passe
        password_hash, salt = auth_service.hash_password(password_data.new_password)
        credentials.password_hash = password_hash
        credentials.salt = salt

        await db.commit()

        logger.info(f"Mot de passe changé pour: {user.email}")

        return BaseResponse(message="Mot de passe changé avec succès")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du changement de mot de passe: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_database)
):
    """
    Récupère les informations de l'utilisateur connecté
    """
    try:
        auth_service = AuthService()

        user = await auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )

        return UserResponse.from_orm(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des infos utilisateur: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )
