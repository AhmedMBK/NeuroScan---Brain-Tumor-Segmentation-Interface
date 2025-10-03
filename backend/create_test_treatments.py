#!/usr/bin/env python3
"""
🧪 Créer des données de test pour les traitements
"""

import asyncio
import uuid
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.database_models import Treatment, Patient, Doctor, User, TreatmentStatus
from config.settings import Settings

settings = Settings()

async def create_test_treatments():
    """Créer des traitements de test"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🧪 === CRÉATION TRAITEMENTS DE TEST ===")
        
        # 1. Trouver tbib et ses patients
        result = await session.execute(
            select(User.id, Doctor.id.label("doctor_id"))
            .join(Doctor, Doctor.user_id == User.id)
            .where(User.email == "tbib@gmail.com")
        )
        tbib_info = result.first()
        
        if not tbib_info:
            print("❌ tbib non trouvé")
            return
        
        print(f"✅ tbib trouvé: Doctor ID = {tbib_info.doctor_id}")
        
        # 2. Trouver les patients assignés à tbib
        result = await session.execute(
            select(Patient.id, Patient.first_name, Patient.last_name)
            .where(Patient.assigned_doctor_id == tbib_info.doctor_id)
        )
        patients = result.all()
        
        if not patients:
            print("❌ Aucun patient assigné à tbib")
            return
        
        print(f"✅ Patients trouvés: {len(patients)}")
        for p in patients:
            print(f"   - {p.first_name} {p.last_name} (ID: {p.id[:8]}...)")
        
        # 3. Créer des traitements variés
        treatments_to_create = []
        
        for i, patient in enumerate(patients):
            # Traitement 1: Chimiothérapie active
            treatments_to_create.append({
                "id": str(uuid.uuid4()),
                "patient_id": patient.id,
                "prescribed_by_doctor_id": tbib_info.doctor_id,
                "treatment_type": "Chimiothérapie",
                "medication_name": "Temozolomide",
                "dosage": "150 mg/m²",
                "frequency": "1 fois par jour",
                "duration": "6 cycles de 28 jours",
                "start_date": date.today() - timedelta(days=30),
                "end_date": date.today() + timedelta(days=150),
                "status": TreatmentStatus.ACTIVE,
                "notes": "Traitement adjuvant post-chirurgie. Surveillance hématologique hebdomadaire.",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            
            # Traitement 2: Radiothérapie terminée
            treatments_to_create.append({
                "id": str(uuid.uuid4()),
                "patient_id": patient.id,
                "prescribed_by_doctor_id": tbib_info.doctor_id,
                "treatment_type": "Radiothérapie",
                "medication_name": None,
                "dosage": "60 Gy en 30 fractions",
                "frequency": "5 séances par semaine",
                "duration": "6 semaines",
                "start_date": date.today() - timedelta(days=120),
                "end_date": date.today() - timedelta(days=78),
                "status": TreatmentStatus.COMPLETED,
                "notes": "Radiothérapie conformationnelle avec modulation d'intensité. Bien tolérée.",
                "created_at": datetime.now() - timedelta(days=120),
                "updated_at": datetime.now() - timedelta(days=78)
            })
            
            # Traitement 3: Traitement symptomatique
            treatments_to_create.append({
                "id": str(uuid.uuid4()),
                "patient_id": patient.id,
                "prescribed_by_doctor_id": tbib_info.doctor_id,
                "treatment_type": "Traitement symptomatique",
                "medication_name": "Dexaméthasone",
                "dosage": "4 mg",
                "frequency": "2 fois par jour",
                "duration": "En continu",
                "start_date": date.today() - timedelta(days=60),
                "end_date": None,
                "status": TreatmentStatus.ACTIVE,
                "notes": "Anti-œdémateux cérébral. Réduction progressive selon tolérance.",
                "created_at": datetime.now() - timedelta(days=60),
                "updated_at": datetime.now()
            })
            
            # Traitement 4: Traitement suspendu
            if i == 0:  # Seulement pour le premier patient
                treatments_to_create.append({
                    "id": str(uuid.uuid4()),
                    "patient_id": patient.id,
                    "prescribed_by_doctor_id": tbib_info.doctor_id,
                    "treatment_type": "Immunothérapie",
                    "medication_name": "Bevacizumab",
                    "dosage": "10 mg/kg",
                    "frequency": "Toutes les 2 semaines",
                    "duration": "12 cycles",
                    "start_date": date.today() - timedelta(days=90),
                    "end_date": date.today() + timedelta(days=60),
                    "status": TreatmentStatus.SUSPENDED,
                    "notes": "Traitement suspendu temporairement en raison d'effets secondaires (hypertension).",
                    "created_at": datetime.now() - timedelta(days=90),
                    "updated_at": datetime.now() - timedelta(days=5)
                })
        
        # 4. Insérer les traitements
        print(f"\n💊 Création de {len(treatments_to_create)} traitements...")
        
        for treatment_data in treatments_to_create:
            treatment = Treatment(**treatment_data)
            session.add(treatment)
        
        await session.commit()
        
        print(f"✅ {len(treatments_to_create)} traitements créés avec succès!")
        
        # 5. Vérifier les traitements créés
        result = await session.execute(
            select(Treatment.treatment_type, Treatment.medication_name, Treatment.status)
            .join(Patient, Treatment.patient_id == Patient.id)
            .where(Patient.assigned_doctor_id == tbib_info.doctor_id)
        )
        created_treatments = result.all()
        
        print(f"\n📋 Traitements créés pour tbib:")
        status_counts = {}
        for t in created_treatments:
            status = str(t.status).replace('TreatmentStatus.', '')
            status_counts[status] = status_counts.get(status, 0) + 1
            print(f"   - {t.treatment_type} | {t.medication_name or 'N/A'} | {status}")
        
        print(f"\n📊 Répartition par statut:")
        for status, count in status_counts.items():
            print(f"   - {status}: {count}")

if __name__ == "__main__":
    asyncio.run(create_test_treatments())
