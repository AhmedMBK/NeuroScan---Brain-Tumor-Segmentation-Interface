#!/usr/bin/env python3
"""
Script pour créer un médecin de test
"""

import asyncio
import asyncpg
import sys
import os
import uuid
import logging
from datetime import datetime

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from services.auth_service import AuthService

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_test_doctor():
    """Crée un médecin de test avec profil complet"""
    
    # Convertir l'URL SQLAlchemy en URL asyncpg
    database_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(database_url)
    
    try:
        logger.info("🔄 Création d'un médecin de test...")
        
        # Données du médecin de test
        user_id = str(uuid.uuid4())
        doctor_id = str(uuid.uuid4())
        
        doctor_data = {
            "first_name": "Dr. Jean",
            "last_name": "Martin",
            "email": "dr.martin@cerebloom.com",
            "username": "dr.martin",
            "password": "password123",
            "phone": "+33123456789",
            "bio": "Neurochirurgien spécialisé en tumeurs cérébrales",
            "office_location": "Bureau 201, Aile Neurologie"
        }
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = await conn.fetchval(
            "SELECT id FROM users WHERE email = $1",
            doctor_data["email"]
        )
        
        if existing_user:
            logger.info(f"✅ L'utilisateur {doctor_data['email']} existe déjà")
            return existing_user
        
        # Générer un employee_id unique
        import random
        employee_id = f"DOC{random.randint(100, 999)}"

        # Vérifier que l'employee_id n'existe pas
        while await conn.fetchval("SELECT id FROM users WHERE employee_id = $1", employee_id):
            employee_id = f"DOC{random.randint(100, 999)}"
        
        # Hasher le mot de passe
        auth_service = AuthService()
        password_hash, salt = auth_service.hash_password(doctor_data["password"])
        
        # Commencer une transaction
        async with conn.transaction():
            # 1. Créer l'utilisateur
            await conn.execute("""
                INSERT INTO users (
                    id, first_name, last_name, email, phone, role, status, 
                    employee_id, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, 
                user_id, doctor_data["first_name"], doctor_data["last_name"],
                doctor_data["email"], doctor_data["phone"], "DOCTOR", "ACTIVE",
                employee_id, datetime.now(), datetime.now()
            )
            
            # 2. Créer les credentials
            await conn.execute("""
                INSERT INTO user_credentials (
                    user_id, username, password_hash, salt
                ) VALUES ($1, $2, $3, $4)
            """, 
                user_id, doctor_data["username"], password_hash, salt
            )
            
            # 3. Créer les permissions
            await conn.execute("""
                INSERT INTO user_permissions (
                    user_id, can_view_patients, can_create_patients, can_edit_patients,
                    can_delete_patients, can_view_segmentations, can_create_segmentations,
                    can_validate_segmentations, can_manage_appointments, can_manage_users,
                    can_view_reports, can_export_data
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """, 
                user_id, True, True, True, False, True, True, True, True, False, True, True
            )
            
            # 4. Créer le profil médecin
            await conn.execute("""
                INSERT INTO doctors (
                    id, user_id, bio, office_location, is_active, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, 
                doctor_id, user_id, doctor_data["bio"], doctor_data["office_location"],
                True, datetime.now(), datetime.now()
            )
        
        logger.info(f"✅ Médecin créé avec succès!")
        logger.info(f"   📧 Email: {doctor_data['email']}")
        logger.info(f"   👤 Username: {doctor_data['username']}")
        logger.info(f"   🔑 Password: {doctor_data['password']}")
        logger.info(f"   🆔 User ID: {user_id}")
        logger.info(f"   🏥 Doctor ID: {doctor_id}")
        
        return user_id
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création du médecin: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    print("🔄 Création d'un médecin de test...")
    asyncio.run(create_test_doctor())
