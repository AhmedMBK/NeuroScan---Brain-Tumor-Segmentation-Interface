#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour créer un rendez-vous avec la secrétaire Azza pour le patient Matheus Cunha
"""

import sys
import uuid
from datetime import datetime, date, time
sys.path.append('.')

from sqlalchemy import create_engine
from models.database_models import User, Doctor, Patient, Appointment, AppointmentStatus
from sqlalchemy.orm import sessionmaker
from config.settings import settings

def create_appointment():
    """Crée un rendez-vous avec Azza pour Matheus Cunha"""
    
    try:
        # Créer une connexion synchrone à PostgreSQL
        sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        engine = create_engine(sync_db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # IDs confirmés depuis l'analyse précédente
        azza_user_id = "7df3362d-430b-47bb-aa6d-1dbf03504fd0"  # Azza (secrétaire)
        matheus_patient_id = "04813c40-0621-4aae-ae7c-e8e7cb0539c3"  # Matheus Cunha
        ruben_doctor_id = "d12b0098-46d5-4277-9a13-0893e68779c1"  # Dr. Ruben Amorim

        # Vérification des entités
        print("=== VÉRIFICATION DES ENTITÉS ===")
        
        # Vérifier Azza
        azza = session.query(User).filter(User.id == azza_user_id).first()
        if not azza:
            print("❌ Utilisateur Azza non trouvé")
            return False
        print(f"✅ Azza trouvée: {azza.first_name} {azza.last_name} ({azza.role})")
        
        # Vérifier Matheus
        matheus = session.query(Patient).filter(Patient.id == matheus_patient_id).first()
        if not matheus:
            print("❌ Patient Matheus non trouvé")
            return False
        print(f"✅ Matheus trouvé: {matheus.first_name} {matheus.last_name}")
        
        # Vérifier Dr. Ruben
        ruben = session.query(Doctor).filter(Doctor.id == ruben_doctor_id).first()
        if not ruben:
            print("❌ Docteur Ruben non trouvé")
            return False
        ruben_user = session.query(User).filter(User.id == ruben.user_id).first()
        print(f"✅ Dr. Ruben trouvé: {ruben_user.first_name} {ruben_user.last_name}")
        
        # Vérifier que Azza est assignée à Ruben
        if azza.assigned_doctor_id != ruben_doctor_id:
            print(f"❌ Azza n'est pas assignée au Dr. Ruben")
            print(f"   Azza assigned_doctor_id: {azza.assigned_doctor_id}")
            print(f"   Ruben doctor_id: {ruben_doctor_id}")
            return False
        print("✅ Azza est bien assignée au Dr. Ruben")
        
        # Vérifier que Matheus est assigné à Ruben
        if matheus.assigned_doctor_id != ruben_doctor_id:
            print(f"❌ Matheus n'est pas assigné au Dr. Ruben")
            print(f"   Matheus assigned_doctor_id: {matheus.assigned_doctor_id}")
            print(f"   Ruben doctor_id: {ruben_doctor_id}")
            return False
        print("✅ Matheus est bien assigné au Dr. Ruben")

        print("\n=== CRÉATION DU RENDEZ-VOUS ===")
        
        # Créer le rendez-vous
        appointment_id = str(uuid.uuid4())
        appointment_date = date(2025, 1, 25)  # 25 janvier 2025
        appointment_time = time(14, 30)  # 14h30
        
        new_appointment = Appointment(
            id=appointment_id,
            patient_id=matheus_patient_id,
            doctor_id=ruben_doctor_id,
            scheduled_by_user_id=azza_user_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status=AppointmentStatus.SCHEDULED,
            notes="Rendez-vous créé par la secrétaire Azza pour consultation de suivi",
            appointment_type="CONSULTATION",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Ajouter à la session et sauvegarder
        session.add(new_appointment)
        session.commit()
        
        print(f"✅ Rendez-vous créé avec succès!")
        print(f"   ID: {appointment_id}")
        print(f"   Patient: {matheus.first_name} {matheus.last_name}")
        print(f"   Docteur: {ruben_user.first_name} {ruben_user.last_name}")
        print(f"   Programmé par: {azza.first_name} {azza.last_name}")
        print(f"   Date: {appointment_date}")
        print(f"   Heure: {appointment_time}")
        print(f"   Status: {new_appointment.status}")
        
        # Vérification finale
        print("\n=== VÉRIFICATION FINALE ===")
        created_appointment = session.query(Appointment).filter(Appointment.id == appointment_id).first()
        if created_appointment:
            print("✅ Rendez-vous confirmé dans la base de données")
            
            # Afficher tous les rendez-vous de Matheus
            print(f"\n=== TOUS LES RENDEZ-VOUS DE {matheus.first_name} {matheus.last_name} ===")
            all_appointments = session.query(Appointment).filter(Appointment.patient_id == matheus_patient_id).all()
            for apt in all_appointments:
                doctor = session.query(Doctor).filter(Doctor.id == apt.doctor_id).first()
                doctor_user = session.query(User).filter(User.id == doctor.user_id).first()
                scheduled_by = session.query(User).filter(User.id == apt.scheduled_by_user_id).first()
                
                print(f"   - {apt.appointment_date} à {apt.appointment_time}")
                print(f"     Docteur: {doctor_user.first_name} {doctor_user.last_name}")
                print(f"     Programmé par: {scheduled_by.first_name} {scheduled_by.last_name}")
                print(f"     Status: {apt.status}")
                print()
        else:
            print("❌ Erreur: Rendez-vous non trouvé après création")
            return False
            
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du rendez-vous: {e}")
        import traceback
        traceback.print_exc()
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

if __name__ == "__main__":
    print("🏥 CereBloom - Création de rendez-vous")
    print("=====================================")
    success = create_appointment()
    if success:
        print("\n🎉 Rendez-vous créé avec succès!")
    else:
        print("\n💥 Échec de la création du rendez-vous")
