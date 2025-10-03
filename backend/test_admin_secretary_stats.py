#!/usr/bin/env python3
"""
🧪 Test des statistiques pour ADMIN et SECRETARY
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
            "email": email,
            "password": password
        }
        
        try:
            async with session.post("http://localhost:8000/api/v1/auth/login", json=login_data) as response:
                if response.status != 200:
                    print(f"❌ Échec connexion {role_name}: {response.status}")
                    response_text = await response.text()
                    print(f"   Détail: {response_text}")
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
                print(f"📊 Statut réponse {role_name}: {response.status}")
                
                if response.status != 200:
                    response_text = await response.text()
                    print(f"❌ Échec stats {role_name}: {response_text}")
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
                
                # Afficher la structure complète pour debug
                print(f"📋 Structure complète {role_name}:")
                print(f"   - Clés: {list(stats.keys())}")
                
                return stats
        
        except Exception as e:
            print(f"❌ Erreur stats {role_name}: {e}")
            return None

async def main():
    """Test des rôles ADMIN et SECRETARY"""
    
    print("🧪 === TEST STATISTIQUES ADMIN & SECRETARY ===")
    print("Vérification de la logique corrigée et suppression des volumes moyens")
    
    # Test ADMIN
    admin_stats = await test_role_stats("admin@cerebloom.com", "admin123", "ADMIN")
    
    # Test SECRETARY  
    secretary_stats = await test_role_stats("azza@gmail.com", "azzaazza", "SECRETARY")
    
    # Test DOCTOR (pour comparaison)
    doctor_stats = await test_role_stats("tbib@gmail.com", "password123", "DOCTOR")
    
    print(f"\n🎯 === COMPARAISON DES RÉSULTATS ===")
    
    if admin_stats:
        admin_total = admin_stats.get('segmentation_counts', {}).get('total', 0)
        print(f"👑 ADMIN voit: {admin_total} segmentations (devrait voir TOUTES)")
    
    if secretary_stats:
        secretary_total = secretary_stats.get('segmentation_counts', {}).get('total', 0)
        print(f"📋 SECRETARY voit: {secretary_total} segmentations (devrait voir celles de son médecin assigné)")
    
    if doctor_stats:
        doctor_total = doctor_stats.get('segmentation_counts', {}).get('total', 0)
        print(f"👨‍⚕️ DOCTOR voit: {doctor_total} segmentations (devrait voir ses patients)")
    
    print(f"\n✅ Logique attendue:")
    print(f"   - ADMIN >= DOCTOR >= SECRETARY (selon les assignations)")
    print(f"   - Tous sans section average_volumes")

if __name__ == "__main__":
    asyncio.run(main())
