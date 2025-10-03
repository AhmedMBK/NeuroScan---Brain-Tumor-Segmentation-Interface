#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour créer un rendez-vous directement dans la base de données
avec la secrétaire Azza pour le patient Matheus Cunha
"""

import sys
sys.path.append('.')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database_models import User, Doctor, Patient, Appointment, AppointmentStatus
from datetime import datetime, date, time
import uuid
import os

# IDs récupérés de l'analyse précédente
AZZA_USER_ID = "7df3362d-430b-47bb-aa6d-1dbf03504fd0"
MATHEUS_PATIENT_ID = "04813c40-0621-4aae-ae7c-e8e7cb0539c3"
RUBEN_DOCTOR_ID = "d12b0098-46d5-4277-9a13-0893e68779c1"

def create_appointment_in_db():
    """Crée un rendez-vous directement dans la base de données"""
    try:
        # Connexion à la base de données PostgreSQL
        DATABASE_URL = "postgresql://cerebloom_user:cerebloom_password@localhost:5432/cerebloom_db"
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        print("🏥 Création d'un rendez-vous avec Azza pour Matheus Cunha")
        print("=" * 60)

        # 1. Vérifier que tous les utilisateurs existent
        print("\n1. Vérification des utilisateurs...")
        
        # Vérifier Azza
        azza = session.query(User).filter(User.id == AZZA_USER_ID).first()
        if not azza:
            print("❌ Utilisateur Azza non trouvé")
            return False
        print(f"✅ Azza trouvée: {azza.first_name} {azza.last_name} ({azza.email})")
        
        # Vérifier Matheus
        matheus = session.query(Patient).filter(Patient.id == MATHEUS_PATIENT_ID).first()
        if not matheus:
            print("❌ Patient Matheus non trouvé")
            return False
        print(f"✅ Matheus trouvé: {matheus.first_name} {matheus.last_name}")
        
        # Vérifier Ruben (docteur)
        ruben_doctor = session.query(Doctor).filter(Doctor.id == RUBEN_DOCTOR_ID).first()
        if not ruben_doctor:
            print("❌ Docteur Ruben non trouvé")
            return False
        
        ruben_user = session.query(User).filter(User.id == ruben_doctor.user_id).first()
        print(f"✅ Docteur Ruben trouvé: {ruben_user.first_name} {ruben_user.last_name}")

        # 2. Vérifier les relations
        print("\n2. Vérification des relations...")
        
        # Vérifier que Azza est assignée à Ruben
        if azza.assigned_doctor_id != RUBEN_DOCTOR_ID:
            print(f"❌ Azza n'est pas assignée au docteur Ruben")
            print(f"   Azza assigned_doctor_id: {azza.assigned_doctor_id}")
            print(f"   Ruben doctor_id: {RUBEN_DOCTOR_ID}")
            return False
        print("✅ Azza est bien assignée au docteur Ruben")
        
        # Vérifier que Matheus est assigné à Ruben
        if matheus.assigned_doctor_id != RUBEN_DOCTOR_ID:
            print(f"❌ Matheus n'est pas assigné au docteur Ruben")
            print(f"   Matheus assigned_doctor_id: {matheus.assigned_doctor_id}")
            print(f"   Ruben doctor_id: {RUBEN_DOCTOR_ID}")
            return False
        print("✅ Matheus est bien assigné au docteur Ruben")

        # 3. Créer le rendez-vous
        print("\n3. Création du rendez-vous...")
        
        appointment_id = str(uuid.uuid4())
        appointment_date = date(2025, 1, 25)  # 25 janvier 2025
        appointment_time = time(14, 30)       # 14h30
        
        new_appointment = Appointment(
            id=appointment_id,
            patient_id=MATHEUS_PATIENT_ID,
            doctor_id=RUBEN_DOCTOR_ID,
            scheduled_by_user_id=AZZA_USER_ID,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status=AppointmentStatus.SCHEDULED,
            notes="Consultation de suivi programmée par la secrétaire Azza",
            appointment_type="CONSULTATION",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        session.add(new_appointment)
        session.commit()
        
        print("✅ Rendez-vous créé avec succès!")
        print(f"   ID: {appointment_id}")
        print(f"   Patient: {matheus.first_name} {matheus.last_name}")
        print(f"   Docteur: {ruben_user.first_name} {ruben_user.last_name}")
        print(f"   Programmé par: {azza.first_name} {azza.last_name}")
        print(f"   Date: {appointment_date}")
        print(f"   Heure: {appointment_time}")
        print(f"   Status: {new_appointment.status.value}")

        # 4. Vérification
        print("\n4. Vérification du rendez-vous créé...")
        
        created_appointment = session.query(Appointment).filter(Appointment.id == appointment_id).first()
        if created_appointment:
            print("✅ Rendez-vous vérifié dans la base de données")
            
            # Afficher les détails complets
            patient = session.query(Patient).filter(Patient.id == created_appointment.patient_id).first()
            doctor = session.query(Doctor).filter(Doctor.id == created_appointment.doctor_id).first()
            doctor_user = session.query(User).filter(User.id == doctor.user_id).first()
            scheduled_by = session.query(User).filter(User.id == created_appointment.scheduled_by_user_id).first()
            
            print(f"\n📋 DÉTAILS DU RENDEZ-VOUS:")
            print(f"   ID: {created_appointment.id}")
            print(f"   Patient: {patient.first_name} {patient.last_name} (ID: {patient.id})")
            print(f"   Docteur: {doctor_user.first_name} {doctor_user.last_name} (ID: {doctor.id})")
            print(f"   Programmé par: {scheduled_by.first_name} {scheduled_by.last_name} (ID: {scheduled_by.id})")
            print(f"   Date: {created_appointment.appointment_date}")
            print(f"   Heure: {created_appointment.appointment_time}")
            print(f"   Status: {created_appointment.status.value}")
            print(f"   Type: {created_appointment.appointment_type}")
            print(f"   Notes: {created_appointment.notes}")
            print(f"   Créé le: {created_appointment.created_at}")
        else:
            print("❌ Erreur: Rendez-vous non trouvé après création")
            return False

        session.close()
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la création du rendez-vous: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = create_appointment_in_db()
    
    if success:
        print("\n🎉 SUCCÈS: Le rendez-vous a été créé avec succès!")
        print("\n✅ RÉSUMÉ:")
        print("   - Secrétaire: Azza (azza@gmail.com)")
        print("   - Patient: Matheus Cunha")
        print("   - Docteur: Ruben Amorim")
        print("   - Date: 25 janvier 2025 à 14h30")
        print("   - Type: Consultation de suivi")
    else:
        print("\n❌ ÉCHEC: Impossible de créer le rendez-vous")

if __name__ == "__main__":
    main()
