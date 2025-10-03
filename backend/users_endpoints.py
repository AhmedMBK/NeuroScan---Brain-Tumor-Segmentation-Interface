#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Endpoints pour la gestion des utilisateurs.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, Query, Depends, status
from users_management import (
    app, users_db, doctors_db, sessions_db,
    User, UserCreate, UserUpdate, UserLogin, UserResponse, UserStatistics,
    Doctor, DoctorCreate, DoctorUpdate, DoctorPublicProfile,
    LoginResponse, UserRole, UserStatus, DoctorSpecialty,
    generate_id, hash_password, generate_salt, verify_password,
    create_access_token, create_refresh_token, get_default_permissions,
    get_permissions_list, is_user_online, get_current_user,
    UserCredentials, MAX_LOGIN_ATTEMPTS, LOCKOUT_DURATION_MINUTES
)

# ==================== ENDPOINTS AUTHENTIFICATION ====================

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Enregistre un nouvel utilisateur."""

    # Vérifier si l'email existe déjà
    for user in users_db.values():
        if user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec cet email existe déjà"
            )

    # Vérifier si le nom d'utilisateur existe déjà
    for user in users_db.values():
        if user.credentials.username == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce nom d'utilisateur est déjà pris"
            )

    # Créer l'utilisateur
    user_id = generate_id()
    salt = generate_salt()
    password_hash = hash_password(user_data.password, salt)
    now = datetime.now()

    # Créer les credentials
    credentials = UserCredentials(
        username=user_data.username,
        password_hash=password_hash,
        salt=salt
    )

    # Obtenir les permissions par défaut
    permissions = get_default_permissions(user_data.role)

    # Créer l'utilisateur
    user = User(
        id=user_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone=user_data.phone,
        gender=user_data.gender,
        date_of_birth=user_data.date_of_birth,
        address=user_data.address,
        role=user_data.role,
        status=user_data.status,
        is_verified=False,
        profile_picture=user_data.profile_picture,
        notes=user_data.notes,
        credentials=credentials,
        permissions=permissions,
        created_at=now,
        updated_at=now,
        created_by="system"  # À remplacer par l'utilisateur actuel
    )

    users_db[user_id] = user

    # Créer la réponse
    user_response = UserResponse(
        user=user,
        doctor_profile=None,
        permissions=get_permissions_list(permissions),
        is_online=False
    )

    return user_response

@app.post("/auth/login", response_model=LoginResponse)
async def login_user(login_data: UserLogin):
    """Connecte un utilisateur."""

    # Trouver l'utilisateur par nom d'utilisateur
    user = None
    for u in users_db.values():
        if u.credentials.username == login_data.username:
            user = u
            break

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect"
        )

    # Vérifier si le compte est verrouillé
    if user.credentials.is_locked:
        if (user.credentials.locked_until and
            user.credentials.locked_until > datetime.now()):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Compte temporairement verrouillé. Réessayez plus tard."
            )
        else:
            # Déverrouiller le compte
            user.credentials.is_locked = False
            user.credentials.locked_until = None
            user.credentials.failed_login_attempts = 0

    # Vérifier le mot de passe
    if not verify_password(login_data.password, user.credentials.salt, user.credentials.password_hash):
        # Incrémenter les tentatives échouées
        user.credentials.failed_login_attempts += 1

        if user.credentials.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
            # Verrouiller le compte
            user.credentials.is_locked = True
            user.credentials.locked_until = datetime.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)

            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Compte verrouillé après {MAX_LOGIN_ATTEMPTS} tentatives échouées"
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect"
        )

    # Vérifier le statut du compte
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte inactif ou suspendu"
        )

    # Réinitialiser les tentatives échouées
    user.credentials.failed_login_attempts = 0
    user.credentials.last_login = datetime.now()

    # Créer les tokens
    access_token, expires_at = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Récupérer le profil médecin si applicable
    doctor_profile = None
    if user.role == UserRole.DOCTOR:
        for doctor in doctors_db.values():
            if doctor.user_id == user.id:
                doctor_profile = doctor
                break

    # Créer la réponse
    user_response = UserResponse(
        user=user,
        doctor_profile=doctor_profile,
        permissions=get_permissions_list(user.permissions),
        is_online=True
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_response,
        expires_at=expires_at
    )

@app.post("/auth/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """Déconnecte l'utilisateur actuel."""

    # Invalider toutes les sessions de l'utilisateur
    sessions_to_remove = []
    for token, session in sessions_db.items():
        if session.user_id == current_user.id:
            sessions_to_remove.append(token)

    for token in sessions_to_remove:
        del sessions_db[token]

    return {"message": "Déconnexion réussie"}

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Récupère les informations de l'utilisateur actuel."""

    # Récupérer le profil médecin si applicable
    doctor_profile = None
    if current_user.role == UserRole.DOCTOR:
        for doctor in doctors_db.values():
            if doctor.user_id == current_user.id:
                doctor_profile = doctor
                break

    return UserResponse(
        user=current_user,
        doctor_profile=doctor_profile,
        permissions=get_permissions_list(current_user.permissions),
        is_online=is_user_online(current_user.id)
    )

# ==================== ENDPOINTS UTILISATEURS ====================

@app.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[UserRole] = Query(None),
    status: Optional[UserStatus] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Récupère la liste des utilisateurs."""

    # Vérifier les permissions
    if not current_user.permissions.can_manage_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission insuffisante"
        )

    users = list(users_db.values())

    # Appliquer les filtres
    if role:
        users = [u for u in users if u.role == role]

    if status:
        users = [u for u in users if u.status == status]

    if search:
        search_lower = search.lower()
        users = [
            u for u in users
            if (search_lower in u.first_name.lower() or
                search_lower in u.last_name.lower() or
                search_lower in u.email.lower() or
                search_lower in u.credentials.username.lower())
        ]

    # Trier par nom
    users.sort(key=lambda x: (x.last_name, x.first_name))

    # Appliquer la pagination
    users = users[skip:skip + limit]

    # Créer les réponses
    user_responses = []
    for user in users:
        doctor_profile = None
        if user.role == UserRole.DOCTOR:
            for doctor in doctors_db.values():
                if doctor.user_id == user.id:
                    doctor_profile = doctor
                    break

        user_responses.append(UserResponse(
            user=user,
            doctor_profile=doctor_profile,
            permissions=get_permissions_list(user.permissions),
            is_online=is_user_online(user.id)
        ))

    return user_responses

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: User = Depends(get_current_user)):
    """Récupère un utilisateur par son ID."""

    # Vérifier les permissions (peut voir son propre profil ou avoir la permission)
    if user_id != current_user.id and not current_user.permissions.can_manage_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission insuffisante"
        )

    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    user = users_db[user_id]

    # Récupérer le profil médecin si applicable
    doctor_profile = None
    if user.role == UserRole.DOCTOR:
        for doctor in doctors_db.values():
            if doctor.user_id == user.id:
                doctor_profile = doctor
                break

    return UserResponse(
        user=user,
        doctor_profile=doctor_profile,
        permissions=get_permissions_list(user.permissions),
        is_online=is_user_online(user.id)
    )
