#!/usr/bin/env python3
"""
Script pour déboguer les profils médecins
"""

import asyncio
import asyncpg
import sys
import os
import logging

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_doctor_profiles():
    """Débogue les profils médecins dans la base de données"""
    
    # Convertir l'URL SQLAlchemy en URL asyncpg
    database_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(database_url)
    
    try:
        logger.info("🔍 Analyse des profils médecins...")
        
        # 1. Lister tous les utilisateurs avec le rôle DOCTOR
        users_doctors = await conn.fetch("""
            SELECT id, first_name, last_name, email, role, employee_id, created_at
            FROM users 
            WHERE role = 'DOCTOR'
            ORDER BY created_at DESC
        """)
        
        logger.info(f"📊 Utilisateurs avec rôle DOCTOR: {len(users_doctors)}")
        for user in users_doctors:
            logger.info(f"   👤 {user['first_name']} {user['last_name']} ({user['email']}) - ID: {user['id']}")
        
        # 2. Lister tous les profils dans la table doctors
        doctor_profiles = await conn.fetch("""
            SELECT d.id, d.user_id, d.bio, d.office_location, d.is_active, d.created_at,
                   u.first_name, u.last_name, u.email
            FROM doctors d
            LEFT JOIN users u ON d.user_id = u.id
            ORDER BY d.created_at DESC
        """)
        
        logger.info(f"📊 Profils dans la table doctors: {len(doctor_profiles)}")
        for profile in doctor_profiles:
            logger.info(f"   🏥 Dr. {profile['first_name']} {profile['last_name']} - User ID: {profile['user_id']}")
            logger.info(f"      Bio: {profile['bio'][:50] if profile['bio'] else 'Aucune'}...")
            logger.info(f"      Bureau: {profile['office_location'] or 'Non défini'}")
            logger.info(f"      Actif: {profile['is_active']}")
        
        # 3. Vérifier les utilisateurs DOCTOR sans profil
        users_without_profile = await conn.fetch("""
            SELECT u.id, u.first_name, u.last_name, u.email
            FROM users u
            LEFT JOIN doctors d ON u.id = d.user_id
            WHERE u.role = 'DOCTOR' AND d.id IS NULL
        """)
        
        logger.info(f"⚠️  Utilisateurs DOCTOR sans profil: {len(users_without_profile)}")
        for user in users_without_profile:
            logger.info(f"   ❌ {user['first_name']} {user['last_name']} ({user['email']}) - ID: {user['id']}")
        
        # 4. Vérifier les profils sans utilisateur (orphelins)
        orphan_profiles = await conn.fetch("""
            SELECT d.id, d.user_id, d.bio
            FROM doctors d
            LEFT JOIN users u ON d.user_id = u.id
            WHERE u.id IS NULL
        """)
        
        logger.info(f"⚠️  Profils orphelins (sans utilisateur): {len(orphan_profiles)}")
        for profile in orphan_profiles:
            logger.info(f"   ❌ Profil ID: {profile['id']} - User ID manquant: {profile['user_id']}")
        
        # 5. Statistiques générales
        total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
        total_doctors = await conn.fetchval("SELECT COUNT(*) FROM doctors")
        
        logger.info(f"📈 Statistiques:")
        logger.info(f"   👥 Total utilisateurs: {total_users}")
        logger.info(f"   🏥 Total profils médecins: {total_doctors}")
        logger.info(f"   ✅ Médecins avec profil: {len(doctor_profiles)}")
        logger.info(f"   ❌ Médecins sans profil: {len(users_without_profile)}")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du débogage: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    print("🔍 Débogage des profils médecins...")
    asyncio.run(debug_doctor_profiles())
