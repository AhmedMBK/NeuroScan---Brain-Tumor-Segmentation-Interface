#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API principale pour la gestion des utilisateurs et médecins.
"""

import uvicorn
from datetime import datetime, timedelta
from users_management import (
    app, users_db, doctors_db,
    User, Doctor, UserRole, UserStatus, DoctorSpecialty, DoctorStatus, Gender,
    UserCredentials, UserPermissions, DoctorEducation, DoctorCertification, DoctorSchedule,
    generate_id, hash_password, generate_salt, get_default_permissions
)

# Importer tous les endpoints
import users_endpoints
import doctors_endpoints

def create_sample_users_and_doctors():
    """Crée des utilisateurs et médecins d'exemple."""
    now = datetime.now()
    
    # Créer un administrateur
    admin_id = generate_id()
    admin_salt = generate_salt()
    admin_password_hash = hash_password("admin123", admin_salt)
    
    admin_credentials = UserCredentials(
        username="admin",
        password_hash=admin_password_hash,
        salt=admin_salt
    )
    
    admin_permissions = get_default_permissions(UserRole.ADMIN)
    
    admin = User(
        id=admin_id,
        first_name="Admin",
        last_name="Système",
        email="admin@cerebloom.com",
        phone="+33123456789",
        gender=Gender.OTHER,
        date_of_birth="1980-01-01",
        address="123 Rue Admin, Paris",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        is_verified=True,
        credentials=admin_credentials,
        permissions=admin_permissions,
        department="Administration",
        employee_id="ADM001",
        created_at=now,
        updated_at=now,
        created_by="system"
    )
    
    users_db[admin_id] = admin
    
    # Créer un médecin neurologue
    doctor_user_id = generate_id()
    doctor_salt = generate_salt()
    doctor_password_hash = hash_password("doctor123", doctor_salt)
    
    doctor_credentials = UserCredentials(
        username="dr.martin",
        password_hash=doctor_password_hash,
        salt=doctor_salt
    )
    
    doctor_permissions = get_default_permissions(UserRole.DOCTOR)
    
    doctor_user = User(
        id=doctor_user_id,
        first_name="Sarah",
        last_name="Martin",
        email="sarah.martin@cerebloom.com",
        phone="+33123456790",
        gender=Gender.FEMALE,
        date_of_birth="1975-03-15",
        address="456 Avenue Médecins, Paris",
        role=UserRole.DOCTOR,
        status=UserStatus.ACTIVE,
        is_verified=True,
        credentials=doctor_credentials,
        permissions=doctor_permissions,
        department="Neurologie",
        employee_id="DOC001",
        created_at=now,
        updated_at=now,
        created_by=admin_id
    )
    
    users_db[doctor_user_id] = doctor_user
    
    # Créer le profil médecin
    doctor_id = generate_id()
    
    doctor_education = [
        DoctorEducation(
            degree="Doctorat en Médecine",
            institution="Université Paris Descartes",
            graduation_year="2000",
            country="France"
        ),
        DoctorEducation(
            degree="Spécialisation en Neurologie",
            institution="Hôpital Pitié-Salpêtrière",
            graduation_year="2005",
            country="France"
        )
    ]
    
    doctor_certifications = [
        DoctorCertification(
            name="Certification Européenne de Neurologie",
            issuing_body="European Board of Neurology",
            issue_date="2005-06-15",
            expiry_date="2025-06-15",
            certificate_number="EBN-2005-1234",
            is_active=True
        )
    ]
    
    doctor_schedule = [
        DoctorSchedule(day_of_week="Lundi", start_time="09:00", end_time="17:00", is_available=True),
        DoctorSchedule(day_of_week="Mardi", start_time="09:00", end_time="17:00", is_available=True),
        DoctorSchedule(day_of_week="Mercredi", start_time="09:00", end_time="17:00", is_available=True),
        DoctorSchedule(day_of_week="Jeudi", start_time="09:00", end_time="17:00", is_available=True),
        DoctorSchedule(day_of_week="Vendredi", start_time="09:00", end_time="15:00", is_available=True),
    ]
    
    doctor = Doctor(
        id=doctor_id,
        user_id=doctor_user_id,
        license_number="FR-NEU-2005-001",
        specialty=DoctorSpecialty.NEUROLOGY,
        sub_specialties=[DoctorSpecialty.NEUROSURGERY],
        years_of_experience=19,
        education=doctor_education,
        certifications=doctor_certifications,
        languages_spoken=["Français", "Anglais", "Espagnol"],
        consultation_fee="150€",
        schedule=doctor_schedule,
        status=DoctorStatus.ACTIVE,
        bio="Dr. Sarah Martin est une neurologue expérimentée spécialisée dans le traitement des tumeurs cérébrales et des troubles neurologiques complexes. Elle a plus de 19 ans d'expérience et est reconnue pour son approche compassionnelle et ses compétences techniques avancées.",
        rating=4.8,
        total_reviews=127,
        created_at=now,
        updated_at=now
    )
    
    doctors_db[doctor_id] = doctor
    
    # Créer un médecin oncologue
    oncologist_user_id = generate_id()
    oncologist_salt = generate_salt()
    oncologist_password_hash = hash_password("onco123", oncologist_salt)
    
    oncologist_credentials = UserCredentials(
        username="dr.dubois",
        password_hash=oncologist_password_hash,
        salt=oncologist_salt
    )
    
    oncologist_user = User(
        id=oncologist_user_id,
        first_name="Michel",
        last_name="Dubois",
        email="michel.dubois@cerebloom.com",
        phone="+33123456791",
        gender=Gender.MALE,
        date_of_birth="1970-08-22",
        address="789 Boulevard Oncologie, Paris",
        role=UserRole.DOCTOR,
        status=UserStatus.ACTIVE,
        is_verified=True,
        credentials=oncologist_credentials,
        permissions=doctor_permissions,
        department="Oncologie",
        employee_id="DOC002",
        created_at=now,
        updated_at=now,
        created_by=admin_id
    )
    
    users_db[oncologist_user_id] = oncologist_user
    
    # Profil médecin oncologue
    oncologist_id = generate_id()
    
    oncologist = Doctor(
        id=oncologist_id,
        user_id=oncologist_user_id,
        license_number="FR-ONC-1998-002",
        specialty=DoctorSpecialty.ONCOLOGY,
        sub_specialties=[],
        years_of_experience=26,
        education=[
            DoctorEducation(
                degree="Doctorat en Médecine",
                institution="Université Lyon 1",
                graduation_year="1998",
                country="France"
            )
        ],
        certifications=[
            DoctorCertification(
                name="Certification en Oncologie Médicale",
                issuing_body="Société Française d'Oncologie",
                issue_date="2001-09-10",
                certificate_number="SFO-2001-5678",
                is_active=True
            )
        ],
        languages_spoken=["Français", "Anglais"],
        consultation_fee="180€",
        schedule=doctor_schedule,
        status=DoctorStatus.ACTIVE,
        bio="Dr. Michel Dubois est un oncologue médical avec plus de 26 ans d'expérience dans le traitement des cancers. Il se spécialise dans les thérapies innovantes et la prise en charge personnalisée des patients.",
        rating=4.9,
        total_reviews=203,
        created_at=now,
        updated_at=now
    )
    
    doctors_db[oncologist_id] = oncologist
    
    # Créer une infirmière
    nurse_id = generate_id()
    nurse_salt = generate_salt()
    nurse_password_hash = hash_password("nurse123", nurse_salt)
    
    nurse_credentials = UserCredentials(
        username="nurse.claire",
        password_hash=nurse_password_hash,
        salt=nurse_salt
    )
    
    nurse_permissions = get_default_permissions(UserRole.NURSE)
    
    nurse = User(
        id=nurse_id,
        first_name="Claire",
        last_name="Rousseau",
        email="claire.rousseau@cerebloom.com",
        phone="+33123456792",
        gender=Gender.FEMALE,
        date_of_birth="1985-12-10",
        address="321 Rue Soins, Paris",
        role=UserRole.NURSE,
        status=UserStatus.ACTIVE,
        is_verified=True,
        credentials=nurse_credentials,
        permissions=nurse_permissions,
        department="Soins",
        employee_id="NUR001",
        created_at=now,
        updated_at=now,
        created_by=admin_id
    )
    
    users_db[nurse_id] = nurse
    
    print("✅ Utilisateurs et médecins d'exemple créés !")
    print(f"   - {len(users_db)} utilisateurs")
    print(f"   - {len(doctors_db)} médecins")
    print("\n👥 Comptes de test :")
    print("   Admin: admin / admin123")
    print("   Médecin 1: dr.martin / doctor123")
    print("   Médecin 2: dr.dubois / onco123")
    print("   Infirmière: nurse.claire / nurse123")

if __name__ == "__main__":
    # Créer les données d'exemple
    create_sample_users_and_doctors()
    
    print("\n🚀 Démarrage de l'API de Gestion des Utilisateurs...")
    print("📖 Documentation: http://localhost:8002/docs")
    print("🔄 API: http://localhost:8002")
    print("\n🔐 Endpoints d'authentification :")
    print("   POST /auth/register - Inscription")
    print("   POST /auth/login - Connexion")
    print("   GET /auth/me - Profil utilisateur")
    print("   POST /auth/logout - Déconnexion")
    print("\n👥 Endpoints utilisateurs :")
    print("   GET /users - Liste des utilisateurs")
    print("   GET /users/{id} - Détails utilisateur")
    print("\n🩺 Endpoints médecins :")
    print("   GET /doctors - Liste publique des médecins")
    print("   GET /doctors/public/{id} - Profil public médecin")
    print("   GET /doctors/by-specialty/{specialty} - Médecins par spécialité")
    
    # Démarrer le serveur
    uvicorn.run(
        "main_users_api:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
