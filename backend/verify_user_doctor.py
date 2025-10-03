#!/usr/bin/env python3
"""
Script pour vérifier la correspondance User <-> Doctor
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

async def verify_user_doctor_mapping():
    """Vérifie la correspondance entre users et doctors"""
    
    # Convertir l'URL SQLAlchemy en URL asyncpg
    database_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(database_url)
    
    try:
        logger.info("🔍 Vérification de la correspondance User <-> Doctor...")
        
        # ID de l'utilisateur Dr. Martin que nous testons
        dr_martin_id = "a47bdb6a-291d-4d5e-bc37-a35104c0a70d"
        
        # 1. Vérifier l'utilisateur Dr. Martin
        user = await conn.fetchrow("""
            SELECT id, first_name, last_name, email, role
            FROM users 
            WHERE id = $1
        """, dr_martin_id)
        
        if user:
            logger.info(f"✅ Utilisateur trouvé:")
            logger.info(f"   🆔 ID: {user['id']}")
            logger.info(f"   👤 Nom: {user['first_name']} {user['last_name']}")
            logger.info(f"   📧 Email: {user['email']}")
            logger.info(f"   🎭 Rôle: {user['role']}")
        else:
            logger.error(f"❌ Utilisateur {dr_martin_id} non trouvé!")
            return
        
        # 2. Chercher le profil médecin correspondant
        doctor = await conn.fetchrow("""
            SELECT id, user_id, bio, office_location, is_active
            FROM doctors 
            WHERE user_id = $1
        """, dr_martin_id)
        
        if doctor:
            logger.info(f"✅ Profil médecin trouvé:")
            logger.info(f"   🏥 Doctor ID: {doctor['id']}")
            logger.info(f"   🔗 User ID: {doctor['user_id']}")
            logger.info(f"   📝 Bio: {doctor['bio'][:50] if doctor['bio'] else 'Aucune'}...")
            logger.info(f"   🏢 Bureau: {doctor['office_location']}")
            logger.info(f"   ✅ Actif: {doctor['is_active']}")
        else:
            logger.error(f"❌ Profil médecin non trouvé pour user_id: {dr_martin_id}")
            
            # Chercher tous les profils médecins pour voir s'il y a un problème
            all_doctors = await conn.fetch("""
                SELECT id, user_id, bio
                FROM doctors
            """)
            
            logger.info(f"📋 Tous les profils médecins ({len(all_doctors)}):")
            for doc in all_doctors:
                logger.info(f"   🏥 Doctor ID: {doc['id']} -> User ID: {doc['user_id']}")
        
        # 3. Vérifier s'il y a des secrétaires assignées
        if doctor:
            secretaries = await conn.fetch("""
                SELECT id, first_name, last_name, email, assigned_doctor_id
                FROM users 
                WHERE role = 'SECRETARY' AND assigned_doctor_id = $1
            """, doctor['id'])
            
            logger.info(f"👩‍💼 Secrétaires assignées: {len(secretaries)}")
            for secretary in secretaries:
                logger.info(f"   - {secretary['first_name']} {secretary['last_name']} ({secretary['email']})")
        
        # 4. Test de la requête exacte de l'endpoint
        logger.info("🧪 Test de la requête exacte de l'endpoint...")
        
        test_result = await conn.fetchrow("""
            SELECT d.id, d.user_id, d.bio, d.office_location, d.is_active
            FROM doctors d
            WHERE d.user_id = $1
        """, dr_martin_id)
        
        if test_result:
            logger.info("✅ Requête de l'endpoint fonctionne!")
            logger.info(f"   Résultat: Doctor ID {test_result['id']}")
        else:
            logger.error("❌ Requête de l'endpoint échoue!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    print("🔍 Vérification User <-> Doctor...")
    asyncio.run(verify_user_doctor_mapping())
