#!/usr/bin/env python3
"""
🧠 CereBloom - Test API Appointments
Test complet de l'API des rendez-vous
"""

import requests
import json
from datetime import datetime, date, time, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@cerebloom.com"
ADMIN_PASSWORD = "admin123"
DOCTOR_EMAIL = "tbib@gmail.com"
DOCTOR_PASSWORD = "tbibtbib"

def login_user(email: str, password: str):
    """Connexion utilisateur"""
    print(f"🔐 Connexion de {email}...")
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Connexion réussie pour {email}")
        return data["access_token"]
    else:
        print(f"❌ Erreur de connexion: {response.text}")
        return None

def get_patients(token: str):
    """Récupérer la liste des patients"""
    print("📋 Récupération des patients...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/patients", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        patients = data.get("items", [])
        print(f"✅ {len(patients)} patients trouvés")
        return patients
    else:
        print(f"❌ Erreur récupération patients: {response.text}")
        return []

def get_doctors(token: str):
    """Récupérer la liste des médecins"""
    print("👨‍⚕️ Récupération des médecins...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/doctors", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        doctors = data.get("doctors", [])
        print(f"✅ {len(doctors)} médecins trouvés")
        return doctors
    else:
        print(f"❌ Erreur récupération médecins: {response.text}")
        return []

def create_appointment(token: str, patient_id: str, doctor_id: str):
    """Créer un rendez-vous de test"""
    print("📅 Création d'un rendez-vous de test...")
    
    # Date de demain à 14h30
    tomorrow = date.today() + timedelta(days=1)
    appointment_time = time(14, 30)
    
    appointment_data = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_date": tomorrow.isoformat(),
        "appointment_time": appointment_time.isoformat(),
        "status": "SCHEDULED",
        "notes": "Consultation de suivi - Test API",
        "appointment_type": "CONSULTATION"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/appointments", 
                           headers=headers, 
                           json=appointment_data)
    
    if response.status_code == 200:
        appointment = response.json()
        print(f"✅ Rendez-vous créé: {appointment['id']}")
        print(f"   📅 Date: {appointment['appointment_date']}")
        print(f"   🕐 Heure: {appointment['appointment_time']}")
        return appointment
    else:
        print(f"❌ Erreur création rendez-vous: {response.text}")
        return None

def get_appointments(token: str):
    """Récupérer la liste des rendez-vous"""
    print("📅 Récupération des rendez-vous...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/appointments", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        appointments = data.get("appointments", [])
        print(f"✅ {len(appointments)} rendez-vous trouvés")
        
        for apt in appointments:
            patient_name = "N/A"
            doctor_name = "N/A"
            
            if apt.get("patient"):
                patient_name = f"{apt['patient']['first_name']} {apt['patient']['last_name']}"
            
            if apt.get("doctor") and apt["doctor"].get("user"):
                doctor_name = f"Dr. {apt['doctor']['user']['first_name']} {apt['doctor']['user']['last_name']}"
            
            print(f"   📅 {apt['appointment_date']} {apt['appointment_time']} - {patient_name} avec {doctor_name}")
            print(f"      Status: {apt['status']} | Type: {apt.get('appointment_type', 'N/A')}")
            if apt.get('notes'):
                print(f"      Notes: {apt['notes']}")
        
        return appointments
    else:
        print(f"❌ Erreur récupération rendez-vous: {response.text}")
        return []

def test_appointments_workflow():
    """Test complet du workflow des rendez-vous"""
    print("🧪 === TEST COMPLET API APPOINTMENTS ===\n")
    
    # 1. Connexion admin
    admin_token = login_user(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not admin_token:
        print("❌ Impossible de se connecter en tant qu'admin")
        return
    
    # 2. Récupérer patients et médecins
    patients = get_patients(admin_token)
    doctors = get_doctors(admin_token)
    
    if not patients:
        print("❌ Aucun patient trouvé")
        return
    
    if not doctors:
        print("❌ Aucun médecin trouvé")
        return
    
    # 3. Prendre le premier patient et médecin
    patient = patients[0]
    doctor = doctors[0]
    
    print(f"\n📋 Patient sélectionné: {patient['first_name']} {patient['last_name']} (ID: {patient['id']})")

    # Gérer le cas où doctor['user'] peut ne pas exister
    if 'user' in doctor and doctor['user']:
        doctor_name = f"Dr. {doctor['user']['first_name']} {doctor['user']['last_name']}"
    else:
        doctor_name = f"Dr. ID-{doctor['id']}"

    print(f"👨‍⚕️ Médecin sélectionné: {doctor_name} (ID: {doctor['id']})")
    
    # 4. Créer un rendez-vous
    appointment = create_appointment(admin_token, patient['id'], doctor['id'])
    
    # 5. Récupérer tous les rendez-vous
    print("\n" + "="*50)
    appointments = get_appointments(admin_token)
    
    # 6. Test avec compte médecin
    print("\n" + "="*50)
    print("🧪 Test avec compte médecin...")
    doctor_token = login_user(DOCTOR_EMAIL, DOCTOR_PASSWORD)
    if doctor_token:
        print("👨‍⚕️ Rendez-vous visibles par le médecin:")
        doctor_appointments = get_appointments(doctor_token)
    
    print("\n✅ Test terminé!")

if __name__ == "__main__":
    test_appointments_workflow()
