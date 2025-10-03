#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour créer un rendez-vous avec la secrétaire Azza pour le patient Matheus Cunha
"""

import requests
import json
from datetime import datetime, date, time

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
AZZA_EMAIL = "azza@gmail.com"
AZZA_PASSWORD = "azzaazza"

# IDs récupérés de la base de données
MATHEUS_PATIENT_ID = "04813c40-0621-4aae-ae7c-e8e7cb0539c3"
RUBEN_DOCTOR_ID = "d12b0098-46d5-4277-9a13-0893e68779c1"

def login_azza():
    """Connexion avec les credentials d'Azza"""
    login_data = {
        "username": AZZA_EMAIL,
        "password": AZZA_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            print("✅ Connexion réussie avec Azza")
            return token
        else:
            print(f"❌ Erreur de connexion: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la connexion: {e}")
        return None

def create_appointment(token):
    """Crée un rendez-vous pour Matheus Cunha"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Données du rendez-vous
    appointment_data = {
        "patient_id": MATHEUS_PATIENT_ID,
        "doctor_id": RUBEN_DOCTOR_ID,
        "appointment_date": "2025-01-25",  # Date future
        "appointment_time": "14:30:00",    # 14h30
        "status": "SCHEDULED",
        "notes": "Consultation de suivi programmée par la secrétaire Azza",
        "appointment_type": "CONSULTATION"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/appointments", json=appointment_data, headers=headers)
        print(f"Create appointment response status: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print("✅ Rendez-vous créé avec succès!")
            print(f"ID du rendez-vous: {result.get('id')}")
            print(f"Date: {result.get('appointment_date')}")
            print(f"Heure: {result.get('appointment_time')}")
            print(f"Patient: Matheus Cunha (ID: {result.get('patient_id')})")
            print(f"Docteur: Ruben Amorim (ID: {result.get('doctor_id')})")
            print(f"Programmé par: Azza (ID: {result.get('scheduled_by_user_id')})")
            return result
        else:
            print(f"❌ Erreur lors de la création: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la création du rendez-vous: {e}")
        return None

def verify_appointment(token, appointment_id):
    """Vérifie que le rendez-vous a été créé"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/appointments/{appointment_id}", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Vérification du rendez-vous:")
            print(f"ID: {result.get('id')}")
            print(f"Patient ID: {result.get('patient_id')}")
            print(f"Doctor ID: {result.get('doctor_id')}")
            print(f"Scheduled by: {result.get('scheduled_by_user_id')}")
            print(f"Date: {result.get('appointment_date')}")
            print(f"Heure: {result.get('appointment_time')}")
            print(f"Status: {result.get('status')}")
            print(f"Notes: {result.get('notes')}")
            return True
        else:
            print(f"❌ Erreur lors de la vérification: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def main():
    print("🏥 Création d'un rendez-vous avec Azza pour Matheus Cunha")
    print("=" * 60)
    
    # 1. Connexion avec Azza
    print("\n1. Connexion avec Azza...")
    token = login_azza()
    
    if not token:
        print("❌ Impossible de se connecter. Arrêt du script.")
        return
    
    # 2. Création du rendez-vous
    print("\n2. Création du rendez-vous...")
    appointment = create_appointment(token)
    
    if not appointment:
        print("❌ Impossible de créer le rendez-vous. Arrêt du script.")
        return
    
    # 3. Vérification
    print("\n3. Vérification du rendez-vous...")
    appointment_id = appointment.get('id')
    if appointment_id:
        verify_appointment(token, appointment_id)
    
    print("\n✅ Script terminé avec succès!")

if __name__ == "__main__":
    main()
