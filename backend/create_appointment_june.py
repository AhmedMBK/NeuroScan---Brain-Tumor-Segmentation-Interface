#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour créer un rendez-vous en juin 2025 (période actuellement affichée)
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# IDs confirmés
AZZA_EMAIL = "azza@gmail.com"
AZZA_PASSWORD = "azzaazza"
MATHEUS_PATIENT_ID = "04813c40-0621-4aae-ae7c-e8e7cb0539c3"
RUBEN_DOCTOR_ID = "d12b0098-46d5-4277-9a13-0893e68779c1"

def login_as_azza():
    """Se connecter en tant qu'Azza"""
    login_data = {
        "email": AZZA_EMAIL,
        "password": AZZA_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
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

def create_appointment_june(token):
    """Créer un rendez-vous en juin 2025"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Rendez-vous pour le 5 juin 2025 (dans la semaine affichée 2-8 juin)
    appointment_data = {
        "patient_id": MATHEUS_PATIENT_ID,
        "doctor_id": RUBEN_DOCTOR_ID,
        "appointment_date": "2025-06-05",  # Jeudi 5 juin 2025
        "appointment_time": "10:00:00",    # 10h00
        "status": "SCHEDULED",
        "notes": "Consultation de contrôle programmée par Azza - Visible dans l'interface",
        "appointment_type": "CONSULTATION"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/appointments", json=appointment_data, headers=headers)
        print(f"Create appointment response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Rendez-vous créé avec succès!")
            print(f"   ID: {data.get('id')}")
            print(f"   Date: {data.get('appointment_date')}")
            print(f"   Heure: {data.get('appointment_time')}")
            print(f"   Patient ID: {data.get('patient_id')}")
            print(f"   Doctor ID: {data.get('doctor_id')}")
            return data
        else:
            print(f"❌ Erreur lors de la création: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return None

def verify_appointments(token):
    """Vérifier tous les rendez-vous"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/appointments", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            appointments = data.get("appointments", [])
            print(f"\n📊 TOTAL: {len(appointments)} rendez-vous")
            
            january_count = 0
            june_count = 0
            
            for apt in appointments:
                date_str = apt.get('appointment_date', '')
                if date_str.startswith('2025-01'):
                    january_count += 1
                elif date_str.startswith('2025-06'):
                    june_count += 1
                    print(f"   📅 Juin: {date_str} à {apt.get('appointment_time')}")
            
            print(f"   📅 Janvier 2025: {january_count} rendez-vous")
            print(f"   📅 Juin 2025: {june_count} rendez-vous")
            
        else:
            print(f"❌ Erreur lors de la vérification: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

def main():
    print("🏥 CereBloom - Création de rendez-vous en juin 2025")
    print("=" * 55)
    
    # Se connecter
    token = login_as_azza()
    if not token:
        print("💥 Impossible de se connecter")
        return
    
    # Créer le rendez-vous
    appointment = create_appointment_june(token)
    if not appointment:
        print("💥 Impossible de créer le rendez-vous")
        return
    
    # Vérifier
    verify_appointments(token)
    
    print("\n🎉 Rendez-vous créé pour la semaine du 2-8 juin 2025!")
    print("   Actualisez la page web pour voir le nouveau rendez-vous.")

if __name__ == "__main__":
    main()
