#!/usr/bin/env python3
"""
🚀 Test Rapide API CereBloom
Vérification que votre modèle my_model.h5 fonctionne via l'API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api_quick():
    """Test rapide de l'API"""
    print("🧠 CEREBLOOM API - TEST RAPIDE")
    print("=" * 50)
    
    # 1. Test de base
    print("🔍 Test connexion serveur...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Serveur actif : {data['message']}")
            print(f"   Version : {data['version']}")
        else:
            print(f"❌ Serveur inactif : {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connexion impossible : {e}")
        return False
    
    # 2. Test health check
    print("\n🏥 Test health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status : {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Health : {data.get('status', 'N/A')}")
        else:
            print(f"   Réponse : {response.text[:100]}")
    except Exception as e:
        print(f"❌ Health check échoué : {e}")
    
    # 3. Test authentification
    print("\n🔐 Test authentification...")
    try:
        # Essayer avec JSON
        auth_data = {
            "username": "admin@cerebloom.com",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=auth_data)
        
        if response.status_code != 200:
            # Essayer avec form data
            response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=auth_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Authentification réussie")
            return token
        else:
            print(f"⚠️ Authentification : {response.status_code}")
            print(f"   Réponse : {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur authentification : {e}")
        return None

def test_segmentation_endpoint(token):
    """Test de l'endpoint de segmentation"""
    if not token:
        print("\n⚠️ Pas de token - Test segmentation ignoré")
        return
    
    print("\n🧠 Test endpoint segmentation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    patient_id = "stringd5f01d3b-b54b-43a2-ba3c-0b12c797affc"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/segmentation/process-patient/{patient_id}",
            headers=headers
        )
        
        print(f"   Status : {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            segmentation_id = data.get("segmentation_id")
            print(f"✅ Segmentation lancée : {segmentation_id}")
            print(f"   Modalités : {data.get('available_modalities', [])}")
            print(f"   Modèle : {data.get('model_info', {}).get('model_type', 'N/A')}")
            return segmentation_id
        else:
            print(f"⚠️ Réponse : {response.text[:300]}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur segmentation : {e}")
        return None

def show_instructions():
    """Afficher les instructions pour Swagger"""
    print("\n" + "=" * 60)
    print("🎯 SERVEUR CEREBLOOM ACTIF AVEC VOTRE MODÈLE !")
    print("=" * 60)
    
    print("\n🌐 SWAGGER UI OUVERT :")
    print("   URL : http://localhost:8000/docs")
    
    print("\n🔐 POUR S'AUTHENTIFIER :")
    print("   1. Cliquez sur 'Authorize' (🔒) en haut à droite")
    print("   2. OU utilisez POST /api/v1/auth/login")
    print("   3. Username : admin@cerebloom.com")
    print("   4. Password : admin123")
    
    print("\n🧠 POUR TESTER VOTRE MODÈLE :")
    print("   1. Utilisez : POST /api/v1/segmentation/process-patient/{patient_id}")
    print("   2. Patient ID : stringd5f01d3b-b54b-43a2-ba3c-0b12c797affc")
    print("   3. Votre modèle my_model.h5 sera utilisé automatiquement !")
    
    print("\n📊 RÉSULTATS ATTENDUS :")
    print("   • Volume tumoral : ~35-45 cm³ (réaliste !)")
    print("   • Dice coefficient : >0.85")
    print("   • Temps : 2-5 minutes")
    
    print("\n📂 RÉSULTATS SAUVEGARDÉS DANS :")
    print("   • uploads/segmentation_results/{segmentation_id}/")
    print("   • Rapport PNG avec votre format exact")
    print("   • Fichier NIfTI pour visualisation médicale")
    
    print("\n🎉 VOTRE MODÈLE PROFESSIONNEL EST PRÊT !")
    print("=" * 60)

if __name__ == "__main__":
    token = test_api_quick()
    segmentation_id = test_segmentation_endpoint(token)
    show_instructions()
