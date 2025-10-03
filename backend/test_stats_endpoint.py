#!/usr/bin/env python3
"""
🧪 Test de l'endpoint des statistiques pour tbib
"""

import asyncio
import aiohttp
import json

async def test_stats_endpoint():
    """Tester l'endpoint des statistiques"""
    
    # 1. Se connecter avec tbib pour obtenir un token
    login_data = {
        "email": "tbib@gmail.com",
        "password": "tbibtbib"
    }
    
    async with aiohttp.ClientSession() as session:
        print("🔐 Connexion avec tbib@gmail.com...")
        
        # Login
        async with session.post("http://localhost:8000/api/v1/auth/login", json=login_data) as response:
            if response.status != 200:
                print(f"❌ Erreur de connexion: {response.status}")
                text = await response.text()
                print(f"Réponse: {text}")
                return
            
            login_result = await response.json()
            token = login_result.get("access_token")
            
            if not token:
                print("❌ Token non reçu")
                print(f"Réponse: {login_result}")
                return
            
            print(f"✅ Token reçu: {token[:20]}...")
        
        # 2. Tester l'endpoint des statistiques
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n📊 Test de l'endpoint des statistiques...")
        async with session.get("http://localhost:8000/api/v1/segmentation/statistics", headers=headers) as response:
            print(f"Status: {response.status}")
            
            if response.status == 200:
                stats = await response.json()
                print("✅ Statistiques reçues:")
                print(json.dumps(stats, indent=2, ensure_ascii=False))
                
                # Analyser les résultats
                counts = stats.get("segmentation_counts", {})
                total = counts.get("total", 0)
                completed = counts.get("completed", 0)
                validated = counts.get("validated", 0)
                
                print(f"\n🎯 Résumé:")
                print(f"   - Total: {total}")
                print(f"   - Terminées: {completed}")
                print(f"   - Validées: {validated}")
                
                if total == 0:
                    print("❌ PROBLÈME: Aucune segmentation trouvée pour tbib")
                else:
                    print("✅ Segmentations trouvées pour tbib")
                    
            else:
                print(f"❌ Erreur: {response.status}")
                text = await response.text()
                print(f"Réponse: {text}")

if __name__ == "__main__":
    asyncio.run(test_stats_endpoint())
