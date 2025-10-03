#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour déboguer les données reçues par le frontend
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

def test_doctor_matching(token):
    """Tester la correspondance des médecins"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🔍 TEST DE CORRESPONDANCE MÉDECIN")
    print("=" * 40)
    
    # 1. Récupérer les infos utilisateur
    user_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    user_data = user_response.json()
    assigned_doctor_id = user_data.get("assigned_doctor_id")
    
    print(f"👤 Utilisateur Azza:")
    print(f"   assigned_doctor_id: {assigned_doctor_id}")
    
    # 2. Récupérer la liste des médecins
    doctors_response = requests.get(f"{BASE_URL}/doctors", headers=headers)
    doctors_data = doctors_response.json()
    
    print(f"\n👨‍⚕️ API Doctors retourne:")
    print(f"   Type: {type(doctors_data)}")
    print(f"   Clés: {list(doctors_data.keys()) if isinstance(doctors_data, dict) else 'N/A'}")
    
    # 3. Extraire le tableau des médecins
    doctors_list = doctors_data.get("doctors", []) if isinstance(doctors_data, dict) else doctors_data
    print(f"\n📋 Liste des médecins:")
    print(f"   Type: {type(doctors_list)}")
    print(f"   Nombre: {len(doctors_list) if isinstance(doctors_list, list) else 'N/A'}")
    
    # 4. Chercher le médecin assigné
    if isinstance(doctors_list, list) and assigned_doctor_id:
        print(f"\n🔍 Recherche du médecin avec ID: {assigned_doctor_id}")
        
        found_doctor = None
        for i, doctor in enumerate(doctors_list):
            doctor_id = doctor.get("id")
            print(f"   Médecin {i+1}: ID = {doctor_id}")
            print(f"   Nom: {doctor.get('first_name')} {doctor.get('last_name')}")
            print(f"   Correspondance: {doctor_id == assigned_doctor_id}")
            
            if doctor_id == assigned_doctor_id:
                found_doctor = doctor
                break
            print()
        
        if found_doctor:
            print(f"\n✅ MÉDECIN TROUVÉ:")
            print(json.dumps(found_doctor, indent=2, default=str))
        else:
            print(f"\n❌ MÉDECIN NON TROUVÉ!")
            print(f"   IDs disponibles:")
            for doctor in doctors_list:
                print(f"   - {doctor.get('id')}")
    else:
        print(f"\n❌ Impossible de faire la recherche:")
        print(f"   doctors_list est une liste: {isinstance(doctors_list, list)}")
        print(f"   assigned_doctor_id existe: {bool(assigned_doctor_id)}")

def simulate_frontend_logic(token):
    """Simuler la logique frontend"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🖥️ SIMULATION LOGIQUE FRONTEND")
    print("=" * 40)
    
    # Simuler ce que fait le frontend
    user_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    userData = user_response.json()
    assigned_doctor_id = userData.get("assigned_doctor_id")
    
    doctors_response = requests.get(f"{BASE_URL}/doctors", headers=headers)
    api_response = doctors_response.json()
    
    # Simuler l'extraction dans le hook useDoctors
    doctors_data = api_response.get("doctors", []) if isinstance(api_response, dict) else api_response
    
    print(f"userData.assigned_doctor_id: {assigned_doctor_id}")
    print(f"doctorsData type: {type(doctors_data)}")
    print(f"doctorsData is array: {isinstance(doctors_data, list)}")
    
    # Simuler le useMemo
    if not doctors_data or not isinstance(doctors_data, list) or not assigned_doctor_id:
        assigned_doctor_info = None
        print(f"assignedDoctorInfo: None (conditions non remplies)")
        print(f"  doctors_data exists: {bool(doctors_data)}")
        print(f"  is array: {isinstance(doctors_data, list)}")
        print(f"  assigned_doctor_id exists: {bool(assigned_doctor_id)}")
    else:
        assigned_doctor_info = next((doc for doc in doctors_data if doc.get("id") == assigned_doctor_id), None)
        print(f"assignedDoctorInfo: {assigned_doctor_info is not None}")
        if assigned_doctor_info:
            print(f"  Nom: {assigned_doctor_info.get('first_name')} {assigned_doctor_info.get('last_name')}")

def main():
    print("🏥 CereBloom - Débogage Frontend")
    print("=" * 45)
    
    # Se connecter
    token = login_as_azza()
    if not token:
        print("💥 Impossible de se connecter")
        return
    
    # Tester la correspondance
    test_doctor_matching(token)
    
    # Simuler la logique frontend
    simulate_frontend_logic(token)

if __name__ == "__main__":
    main()
