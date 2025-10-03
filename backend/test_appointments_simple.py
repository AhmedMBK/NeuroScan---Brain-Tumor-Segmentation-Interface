#!/usr/bin/env python3
"""
🧠 CereBloom - Test Simple API Appointments
Test de base pour vérifier la logique des rendez-vous
"""

import requests
import json
from datetime import datetime, date, time, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

def test_appointments_basic():
    """Test de base des appointments"""
    print("🧪 === TEST SIMPLE APPOINTMENTS ===\n")
    
    # 1. Login admin
    print("🔐 Connexion admin...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@cerebloom.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Erreur login: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Connexion réussie")
    
    # 2. Test GET /appointments
    print("\n📅 Test récupération appointments...")
    appointments_response = requests.get(f"{BASE_URL}/appointments", headers=headers)
    
    print(f"Status: {appointments_response.status_code}")
    if appointments_response.status_code == 200:
        data = appointments_response.json()
        print(f"✅ Structure réponse: {list(data.keys())}")
        appointments = data.get("appointments", [])
        print(f"✅ Nombre d'appointments: {len(appointments)}")
        
        if appointments:
            apt = appointments[0]
            print(f"✅ Structure appointment: {list(apt.keys())}")
            print(f"   - ID: {apt.get('id', 'N/A')}")
            print(f"   - Patient ID: {apt.get('patient_id', 'N/A')}")
            print(f"   - Doctor ID: {apt.get('doctor_id', 'N/A')}")
            print(f"   - Date: {apt.get('appointment_date', 'N/A')}")
            print(f"   - Heure: {apt.get('appointment_time', 'N/A')}")
            print(f"   - Status: {apt.get('status', 'N/A')}")
            
            # Vérifier les relations
            if apt.get('patient'):
                print(f"   - Patient: {apt['patient']['first_name']} {apt['patient']['last_name']}")
            if apt.get('doctor') and apt['doctor'].get('user'):
                print(f"   - Médecin: Dr. {apt['doctor']['user']['first_name']} {apt['doctor']['user']['last_name']}")
    else:
        print(f"❌ Erreur: {appointments_response.text}")
    
    # 3. Test récupération patients et médecins pour création
    print("\n📋 Test récupération patients...")
    patients_response = requests.get(f"{BASE_URL}/patients", headers=headers)
    if patients_response.status_code == 200:
        patients = patients_response.json().get("items", [])
        print(f"✅ {len(patients)} patients disponibles")
    else:
        print(f"❌ Erreur patients: {patients_response.text}")
        return
    
    print("\n👨‍⚕️ Test récupération médecins...")
    doctors_response = requests.get(f"{BASE_URL}/doctors", headers=headers)
    if doctors_response.status_code == 200:
        doctors = doctors_response.json().get("doctors", [])
        print(f"✅ {len(doctors)} médecins disponibles")
    else:
        print(f"❌ Erreur médecins: {doctors_response.text}")
        return
    
    # 4. Test création appointment (si données disponibles)
    if patients and doctors:
        print("\n📅 Test création appointment...")
        
        patient_id = patients[0]["id"]
        doctor_id = doctors[0]["id"]
        tomorrow = date.today() + timedelta(days=1)
        
        new_appointment = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_date": tomorrow.isoformat(),
            "appointment_time": "14:30:00",
            "status": "SCHEDULED",
            "notes": "Test API - Consultation de suivi",
            "appointment_type": "CONSULTATION"
        }
        
        create_response = requests.post(f"{BASE_URL}/appointments", 
                                      headers=headers, 
                                      json=new_appointment)
        
        print(f"Status création: {create_response.status_code}")
        if create_response.status_code == 200:
            created_apt = create_response.json()
            print(f"✅ Appointment créé: {created_apt['id']}")
            print(f"   Date: {created_apt['appointment_date']}")
            print(f"   Heure: {created_apt['appointment_time']}")
        else:
            print(f"❌ Erreur création: {create_response.text}")
    
    print("\n✅ Test terminé!")

if __name__ == "__main__":
    test_appointments_basic()
