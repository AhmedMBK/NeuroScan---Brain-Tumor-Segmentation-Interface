#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour déboguer la réponse de l'API appointments
"""

import requests
import json
from datetime import datetime, date
from dateutil.parser import parse

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

def debug_appointments_api(token):
    """Déboguer l'API appointments en détail"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🔍 DÉBOGAGE DE L'API APPOINTMENTS")
    print("=" * 40)
    
    try:
        # Test avec l'URL exacte utilisée par le frontend
        response = requests.get(f"{BASE_URL}/appointments", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 STRUCTURE DE LA RÉPONSE:")
            print(f"Type: {type(data)}")
            print(f"Clés: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            
            appointments = data.get("appointments", [])
            print(f"\n📅 RENDEZ-VOUS TROUVÉS: {len(appointments)}")
            
            for i, apt in enumerate(appointments, 1):
                print(f"\n--- RENDEZ-VOUS {i} ---")
                print(f"Structure complète:")
                print(json.dumps(apt, indent=2, default=str))
                
                # Analyse des dates
                apt_date = apt.get('appointment_date')
                apt_time = apt.get('appointment_time')
                
                print(f"\n📅 ANALYSE DES DATES:")
                print(f"appointment_date (brut): {apt_date} (type: {type(apt_date)})")
                print(f"appointment_time (brut): {apt_time} (type: {type(apt_time)})")
                
                # Test de parsing des dates
                try:
                    if apt_date:
                        parsed_date = parse(apt_date) if isinstance(apt_date, str) else apt_date
                        print(f"Date parsée: {parsed_date}")
                        print(f"Date ISO: {parsed_date.isoformat()}")
                        
                        # Vérifier si c'est dans la semaine du 20-26 janvier 2025
                        week_start = date(2025, 1, 20)
                        week_end = date(2025, 1, 26)
                        apt_date_only = parsed_date.date() if hasattr(parsed_date, 'date') else parsed_date
                        
                        print(f"Dans la semaine 20-26 jan 2025: {week_start <= apt_date_only <= week_end}")
                        
                except Exception as e:
                    print(f"Erreur parsing date: {e}")
                
                # Vérifier les informations patient/docteur
                patient_info = apt.get('patient')
                doctor_info = apt.get('doctor')
                
                print(f"\n👤 PATIENT INFO:")
                if patient_info:
                    print(f"  Nom: {patient_info.get('first_name')} {patient_info.get('last_name')}")
                    print(f"  ID: {patient_info.get('id')}")
                else:
                    print("  Aucune info patient")
                
                print(f"\n👨‍⚕️ DOCTOR INFO:")
                if doctor_info:
                    if doctor_info.get('user'):
                        doctor_user = doctor_info['user']
                        print(f"  Nom: {doctor_user.get('first_name')} {doctor_user.get('last_name')}")
                    print(f"  ID: {doctor_info.get('id')}")
                else:
                    print("  Aucune info docteur")
                
                print(f"\n📋 STATUS & NOTES:")
                print(f"  Status: {apt.get('status')}")
                print(f"  Type: {apt.get('appointment_type')}")
                print(f"  Notes: {apt.get('notes')}")
                
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors du débogage: {e}")
        import traceback
        traceback.print_exc()

def test_frontend_filtering():
    """Simuler le filtrage frontend"""
    print(f"\n🔧 SIMULATION DU FILTRAGE FRONTEND")
    print("=" * 40)
    
    # Simuler les dates de la semaine affichée
    from datetime import datetime, timedelta
    
    # Semaine du 20-26 janvier 2025 (comme affiché dans l'interface)
    week_start = datetime(2025, 1, 20)
    week_end = datetime(2025, 1, 26)
    
    print(f"Période affichée: {week_start.strftime('%d %b')} - {week_end.strftime('%d %b %Y')}")
    
    # Date du rendez-vous créé
    appointment_date = datetime(2025, 1, 25, 14, 30)
    
    print(f"Date du rendez-vous: {appointment_date.strftime('%d %b %Y à %H:%M')}")
    print(f"Dans la période: {week_start <= appointment_date <= week_end}")

def main():
    print("🏥 CereBloom - Débogage des rendez-vous")
    print("=" * 45)
    
    # Se connecter
    token = login_as_azza()
    if not token:
        print("💥 Impossible de se connecter")
        return
    
    # Déboguer l'API
    debug_appointments_api(token)
    
    # Tester le filtrage
    test_frontend_filtering()

if __name__ == "__main__":
    main()
