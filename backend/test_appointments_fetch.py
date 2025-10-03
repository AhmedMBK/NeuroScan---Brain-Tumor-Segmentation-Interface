#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour tester la récupération des rendez-vous via l'API
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def login_as_azza():
    """Se connecter en tant qu'Azza"""
    login_data = {
        "email": "azza@gmail.com",
        "password": "azzaazza"
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

def get_appointments(token):
    """Récupérer tous les rendez-vous"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/appointments", headers=headers)
        print(f"Get appointments response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            appointments = data.get("appointments", [])
            print(f"✅ {len(appointments)} rendez-vous récupérés")
            
            for i, apt in enumerate(appointments, 1):
                print(f"\n--- Rendez-vous {i} ---")
                print(f"ID: {apt.get('id')}")
                print(f"Patient ID: {apt.get('patient_id')}")
                print(f"Doctor ID: {apt.get('doctor_id')}")
                print(f"Date: {apt.get('appointment_date')}")
                print(f"Heure: {apt.get('appointment_time')}")
                print(f"Status: {apt.get('status')}")
                print(f"Notes: {apt.get('notes')}")
                print(f"Type: {apt.get('appointment_type')}")
                
                # Informations patient et docteur si disponibles
                if apt.get('patient'):
                    patient = apt['patient']
                    print(f"Patient: {patient.get('first_name')} {patient.get('last_name')}")
                
                if apt.get('doctor'):
                    doctor = apt['doctor']
                    if doctor.get('user'):
                        doctor_user = doctor['user']
                        print(f"Docteur: {doctor_user.get('first_name')} {doctor_user.get('last_name')}")
            
            return appointments
        else:
            print(f"❌ Erreur lors de la récupération: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération: {e}")
        return []

def test_appointment_filtering():
    """Tester le filtrage des rendez-vous"""
    print("🔍 Test de récupération des rendez-vous avec Azza")
    print("=" * 50)
    
    # Se connecter
    token = login_as_azza()
    if not token:
        print("💥 Impossible de se connecter")
        return
    
    # Récupérer les rendez-vous
    appointments = get_appointments(token)
    
    if not appointments:
        print("⚠️ Aucun rendez-vous trouvé")
        return
    
    # Analyser les rendez-vous
    print(f"\n📊 ANALYSE DES RENDEZ-VOUS")
    print("=" * 30)
    
    january_appointments = []
    june_appointments = []
    other_appointments = []
    
    for apt in appointments:
        date_str = apt.get('appointment_date', '')
        if date_str.startswith('2025-01'):
            january_appointments.append(apt)
        elif date_str.startswith('2025-06'):
            june_appointments.append(apt)
        else:
            other_appointments.append(apt)
    
    print(f"📅 Rendez-vous en janvier 2025: {len(january_appointments)}")
    print(f"📅 Rendez-vous en juin 2025: {len(june_appointments)}")
    print(f"📅 Autres rendez-vous: {len(other_appointments)}")
    
    # Vérifier le rendez-vous créé
    target_appointment = None
    for apt in january_appointments:
        if apt.get('appointment_date') == '2025-01-25':
            target_appointment = apt
            break
    
    if target_appointment:
        print(f"\n✅ RENDEZ-VOUS DU 25 JANVIER TROUVÉ!")
        print(f"   ID: {target_appointment.get('id')}")
        print(f"   Date: {target_appointment.get('appointment_date')}")
        print(f"   Heure: {target_appointment.get('appointment_time')}")
        print(f"   Status: {target_appointment.get('status')}")
    else:
        print(f"\n❌ RENDEZ-VOUS DU 25 JANVIER NON TROUVÉ!")
        print("   Vérifiez si le rendez-vous a bien été créé en base")

if __name__ == "__main__":
    test_appointment_filtering()
