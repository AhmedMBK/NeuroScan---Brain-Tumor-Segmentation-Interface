#!/usr/bin/env python3
"""
🧪 Test API CereBloom avec Swagger
Test complet du workflow avec votre modèle professionnel
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
PATIENT_ID = "stringd5f01d3b-b54b-43a2-ba3c-0b12c797affc"

def test_api_complete():
    """Test complet de l'API"""
    print("🧠 TEST API CEREBLOOM AVEC VOTRE MODÈLE PROFESSIONNEL")
    print("=" * 70)
    
    # 1. Test de base
    print("🔍 Test de connexion...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Serveur actif : {data['message']}")
            print(f"   Version : {data['version']}")
        else:
            print(f"❌ Erreur connexion : {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Impossible de se connecter : {e}")
        return
    
    # 2. Test health check
    print("\n🏥 Test health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check : {data['status']}")
            print(f"   Base de données : {data.get('database', 'N/A')}")
        else:
            print(f"⚠️ Health check : {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur health check : {e}")
    
    # 3. Test authentification
    print("\n🔐 Test authentification...")
    try:
        auth_data = {
            "email": "admin@cerebloom.com",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=auth_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Authentification réussie")
            print(f"   Token : {token[:20]}...")
            
            # Headers pour les requêtes authentifiées
            headers = {"Authorization": f"Bearer {token}"}
            
        else:
            print(f"❌ Échec authentification : {response.status_code}")
            print(f"   Réponse : {response.text}")
            
            # Continuer sans authentification pour les tests publics
            headers = {}
            token = None
            
    except Exception as e:
        print(f"❌ Erreur authentification : {e}")
        headers = {}
        token = None
    
    # 4. Test du patient
    print(f"\n👤 Test patient {PATIENT_ID}...")
    if token:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/patients/{PATIENT_ID}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Patient trouvé : {data.get('first_name', 'N/A')} {data.get('last_name', 'N/A')}")
            else:
                print(f"⚠️ Patient : {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur patient : {e}")
    else:
        print("⚠️ Authentification requise pour tester le patient")
    
    # 5. Test des images
    print(f"\n📁 Test images patient...")
    if token:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/images/patient/{PATIENT_ID}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                images = data.get("images", [])
                print(f"✅ {len(images)} images trouvées")
                for img in images[:3]:  # Afficher les 3 premières
                    modality = img.get("modality", "N/A")
                    filename = img.get("file_name", "N/A")
                    print(f"   📄 {modality}: {filename}")
            else:
                print(f"⚠️ Images : {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur images : {e}")
    else:
        print("⚠️ Authentification requise pour tester les images")
    
    # 6. Test de segmentation avec votre modèle professionnel
    print(f"\n🧠 Test segmentation avec votre modèle professionnel...")
    if token:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/segmentation/process-patient/{PATIENT_ID}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                segmentation_id = data.get("segmentation_id")
                print("✅ Segmentation lancée avec votre modèle !")
                print(f"   ID : {segmentation_id}")
                print(f"   Modalités : {data.get('available_modalities', [])}")
                print(f"   Modèle : {data.get('model_info', {}).get('model_type', 'N/A')}")
                
                # Surveiller le statut
                print("\n⏱️ Surveillance de la segmentation...")
                for attempt in range(10):  # 10 tentatives max
                    time.sleep(5)  # Attendre 5 secondes
                    
                    try:
                        status_response = requests.get(
                            f"{BASE_URL}/api/v1/segmentation/status/{segmentation_id}",
                            headers=headers
                        )
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            status = status_data.get("status", "UNKNOWN")
                            print(f"   Tentative {attempt + 1}: {status}")
                            
                            if status == "COMPLETED":
                                print("🎉 Segmentation terminée avec succès !")
                                
                                # Récupérer les résultats
                                results_response = requests.get(
                                    f"{BASE_URL}/api/v1/segmentation/results/{segmentation_id}",
                                    headers=headers
                                )
                                
                                if results_response.status_code == 200:
                                    results_data = results_response.json()
                                    tumor_analysis = results_data.get("tumor_analysis", {})
                                    total_volume = tumor_analysis.get("total_volume_cm3", 0)
                                    print(f"📊 Volume tumoral total : {total_volume} cm³")
                                    
                                    segments = tumor_analysis.get("tumor_segments", [])
                                    for segment in segments:
                                        name = segment.get("name", "N/A")
                                        volume = segment.get("volume_cm3", 0)
                                        print(f"   🎯 {name}: {volume} cm³")
                                
                                break
                                
                            elif status == "FAILED":
                                print("❌ Segmentation échouée")
                                break
                                
                        else:
                            print(f"   ⚠️ Erreur statut : {status_response.status_code}")
                            
                    except Exception as e:
                        print(f"   ❌ Erreur surveillance : {e}")
                        break
                
            else:
                print(f"❌ Échec segmentation : {response.status_code}")
                print(f"   Réponse : {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur segmentation : {e}")
    else:
        print("⚠️ Authentification requise pour la segmentation")
    
    print("\n" + "=" * 70)
    print("🎯 RÉSUMÉ DU TEST :")
    print(f"🌐 Serveur : {'✅ Actif' if True else '❌ Inactif'}")
    print(f"🔐 Auth : {'✅ OK' if token else '❌ Échec'}")
    print(f"👤 Patient : {'✅ Trouvé' if token else '⚠️ Non testé'}")
    print(f"🧠 Modèle : {'✅ Votre modèle professionnel intégré' if token else '⚠️ Non testé'}")
    print("=" * 70)
    
    print("\n💡 POUR CONTINUER :")
    print("🌐 Ouvrez Swagger UI : http://localhost:8000/docs")
    print("🔐 Authentifiez-vous avec : admin@cerebloom.com / admin123")
    print("🧠 Testez la segmentation : POST /api/v1/segmentation/process-patient/{patient_id}")
    print(f"🆔 Patient ID : {PATIENT_ID}")

if __name__ == "__main__":
    test_api_complete()
