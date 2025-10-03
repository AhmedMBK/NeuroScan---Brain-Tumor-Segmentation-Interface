#!/usr/bin/env python3
"""
Script pour tester l'endpoint my-secretaries
"""

import asyncio
import aiohttp
import json
import sys
import os
import logging

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_my_secretaries_endpoint():
    """Teste l'endpoint my-secretaries avec un médecin connu"""
    
    base_url = "http://localhost:8000/api/v1"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Se connecter avec le Dr. Martin (créé par notre script)
            login_data = {
                "email": "dr.martin@cerebloom.com",
                "password": "password123"
            }
            
            logger.info("🔐 Connexion avec Dr. Martin...")
            async with session.post(f"{base_url}/auth/login", json=login_data) as response:
                if response.status != 200:
                    logger.error(f"❌ Échec de la connexion: {response.status}")
                    text = await response.text()
                    logger.error(f"Réponse: {text}")
                    return
                
                login_result = await response.json()
                token = login_result.get("access_token")
                logger.info("✅ Connexion réussie!")
            
            # 2. Tester l'endpoint my-secretaries
            headers = {"Authorization": f"Bearer {token}"}
            
            logger.info("🔍 Test de l'endpoint my-secretaries...")
            async with session.get(f"{base_url}/doctors/my-secretaries", headers=headers) as response:
                logger.info(f"📊 Statut de la réponse: {response.status}")
                
                response_text = await response.text()
                logger.info(f"📄 Réponse brute: {response_text}")
                
                if response.status == 200:
                    result = await response.json()
                    logger.info("✅ Endpoint fonctionne!")
                    logger.info(f"   🏥 Médecin: {result.get('doctor_name', 'Non défini')}")
                    logger.info(f"   👩‍💼 Nombre de secrétaires: {result.get('secretaries_count', 0)}")
                    
                    secretaries = result.get('secretaries', [])
                    if secretaries:
                        logger.info("   📋 Secrétaires:")
                        for secretary in secretaries:
                            logger.info(f"      - {secretary.get('first_name')} {secretary.get('last_name')}")
                    else:
                        logger.info("   📋 Aucune secrétaire assignée")
                else:
                    logger.error(f"❌ Erreur {response.status}: {response_text}")
            
            # 3. Tester aussi l'endpoint /auth/me pour vérifier l'utilisateur connecté
            logger.info("🔍 Vérification de l'utilisateur connecté...")
            async with session.get(f"{base_url}/auth/me", headers=headers) as response:
                if response.status == 200:
                    user_info = await response.json()
                    logger.info("✅ Utilisateur connecté:")
                    logger.info(f"   👤 Nom: {user_info.get('first_name')} {user_info.get('last_name')}")
                    logger.info(f"   📧 Email: {user_info.get('email')}")
                    logger.info(f"   🎭 Rôle: {user_info.get('role')}")
                    logger.info(f"   🆔 ID: {user_info.get('id')}")
                else:
                    logger.error(f"❌ Erreur lors de la récupération de l'utilisateur: {response.status}")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    print("🧪 Test de l'endpoint my-secretaries...")
    asyncio.run(test_my_secretaries_endpoint())
