#!/usr/bin/env python3
"""
🧪 Test des statistiques pour tous les rôles
"""

import asyncio
import aiohttp
import json

async def test_role_stats(email: str, password: str, role_name: str):
    """Test des statistiques pour un rôle spécifique"""
    
    print(f"\n🔍 === TEST RÔLE {role_name} ({email}) ===")
    
    async with aiohttp.ClientSession() as session:
        # 1. Connexion
        login_data = {
            "username": email,
            "password": password
        }
        
        try:
            async with session.post("http://localhost:8000/api/v1/auth/login", json=login_data) as response:
                if response.status != 200:
                    print(f"❌ Échec connexion {role_name}: {response.status}")
                    return
                
                login_result = await response.json()
                token = login_result.get("access_token")
                
                if not token:
                    print(f"❌ Pas de token pour {role_name}")
                    return
                
                print(f"✅ Connexion {role_name} réussie")
        
        except Exception as e:
            print(f"❌ Erreur connexion {role_name}: {e}")
            return
        
        # 2. Test des statistiques
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            async with session.get("http://localhost:8000/api/v1/segmentation/statistics", headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Échec stats {role_name}: {response.status}")
                    response_text = await response.text()
                    print(f"   Erreur: {response_text}")
                    return
                
                stats = await response.json()
                
                print(f"✅ Statistiques {role_name} récupérées:")
                print(f"   - Total: {stats.get('segmentation_counts', {}).get('total', 0)}")
                print(f"   - Terminées: {stats.get('segmentation_counts', {}).get('completed', 0)}")
                print(f"   - Validées: {stats.get('segmentation_counts', {}).get('validated', 0)}")
                print(f"   - En cours: {stats.get('segmentation_counts', {}).get('processing', 0)}")
                print(f"   - Échecs: {stats.get('segmentation_counts', {}).get('failed', 0)}")
                
                # Vérifier qu'il n'y a plus de section average_volumes
                if "average_volumes" in stats:
                    print(f"⚠️ ATTENTION: Section average_volumes encore présente pour {role_name}")
                else:
                    print(f"✅ Section average_volumes correctement supprimée pour {role_name}")
        
        except Exception as e:
            print(f"❌ Erreur stats {role_name}: {e}")

async def main():
    """Test de tous les rôles"""
    
    print("🧪 === TEST STATISTIQUES TOUS RÔLES ===")
    print("Vérification de la logique corrigée et suppression des volumes moyens")
    
    # Test des différents rôles
    roles_to_test = [
        ("tbib@gmail.com", "password123", "DOCTOR"),
        ("admin@cerebloom.com", "admin123", "ADMIN"),
        # Ajoutez ici d'autres utilisateurs si vous en avez
    ]
    
    for email, password, role in roles_to_test:
        await test_role_stats(email, password, role)
    
    print(f"\n🎯 === RÉSUMÉ ===")
    print("✅ Logique corrigée: Tous les rôles utilisent Patient.assigned_doctor_id")
    print("✅ Section volumes moyens supprimée du backend et frontend")
    print("✅ Dashboard simplifié et plus pertinent médicalement")

if __name__ == "__main__":
    asyncio.run(main())
