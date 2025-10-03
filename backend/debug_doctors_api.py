#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour déboguer l'API des médecins
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def login_as_azza():
    """Se connecter en tant qu'Azza"""
    login_data = {
        "email": "azza@gmail.com",
        "password": "azzaazza"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Connexion réussie en tant qu'Azza")
            return data.get("access_token")
        else:
            print(f"❌ Échec de connexion: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur lors de la connexion: {e}")
        return None

def debug_doctors_api(token):
    """Déboguer l'API des médecins"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🔍 DÉBOGAGE DE L'API DOCTORS")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/doctors", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 STRUCTURE DE LA RÉPONSE:")
            print(f"Type: {type(data)}")
            
            if isinstance(data, list):
                print(f"Nombre de médecins: {len(data)}")
                for i, doctor in enumerate(data, 1):
                    print(f"\n--- MÉDECIN {i} ---")
                    print(json.dumps(doctor, indent=2, default=str))
            elif isinstance(data, dict):
                print(f"Clés: {list(data.keys())}")
                print(f"Contenu:")
                print(json.dumps(data, indent=2, default=str))
            else:
                print(f"Type inattendu: {type(data)}")
                print(f"Contenu: {data}")
                
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors du débogage: {e}")
        import traceback
        traceback.print_exc()

def debug_user_info(token):
    """Déboguer les informations utilisateur d'Azza"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🔍 INFORMATIONS UTILISATEUR AZZA")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"Données utilisateur:")
            print(json.dumps(user_data, indent=2, default=str))
            
            assigned_doctor_id = user_data.get("assigned_doctor_id")
            print(f"\n🎯 assigned_doctor_id: {assigned_doctor_id}")
            
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    print("🏥 CereBloom - Débogage API Médecins")
    print("=" * 45)
    
    # Se connecter
    token = login_as_azza()
    if not token:
        print("💥 Impossible de se connecter")
        return
    
    # Déboguer l'API médecins
    debug_doctors_api(token)
    
    # Déboguer les infos utilisateur
    debug_user_info(token)

if __name__ == "__main__":
    main()
