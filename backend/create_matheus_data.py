#!/usr/bin/env python3
"""
🧪 Créer des données complètes pour Matheus Cunha
"""

import asyncio
import uuid
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.database_models import (
    User, Patient, Doctor, Treatment, TreatmentStatus, 
    AISegmentation, SegmentationStatus, MedicalImage
)
from config.settings import Settings

settings = Settings()

async def create_matheus_complete_data():
    """Créer des données complètes pour Matheus Cunha"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🧪 === CRÉATION DONNÉES COMPLÈTES MATHEUS CUNHA ===")
        
        # 1. Trouver tbib
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
        
        # 2. Créer ou trouver le patient Matheus Cunha
        result = await session.execute(
            select(Patient).where(
                Patient.first_name == "Matheus",
                Patient.last_name == "Cunha"
            )
        )
        matheus = result.scalar_one_or_none()
        
        if not matheus:
            # Créer Matheus
            matheus_id = str(uuid.uuid4())
            matheus = Patient(
                id=matheus_id,
                first_name="Matheus",
                last_name="Cunha",
                date_of_birth=date(1985, 3, 15),
                gender="M",
                phone_number="+33 6 12 34 56 78",
                email="matheus.cunha@email.com",
                address="123 Rue de la Santé, 75014 Paris",
                emergency_contact_name="Maria Cunha",
                emergency_contact_phone="+33 6 87 65 43 21",
                medical_history="Antécédents familiaux de tumeurs cérébrales",
                assigned_doctor_id=tbib_info.doctor_id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(matheus)
            await session.commit()
            print(f"✅ Patient Matheus Cunha créé: {matheus_id}")
        else:
            # Assigner à tbib si pas déjà fait
            if matheus.assigned_doctor_id != tbib_info.doctor_id:
                matheus.assigned_doctor_id = tbib_info.doctor_id
                await session.commit()
            print(f"✅ Patient Matheus Cunha trouvé: {matheus.id}")
        
        # 3. Créer des traitements variés
        treatments_data = [
            {
                "treatment_type": "Chirurgie",
                "medication_name": None,
                "dosage": "Résection tumorale complète",
                "frequency": "Intervention unique",
                "duration": "3 heures",
                "start_date": date.today() - timedelta(days=180),
                "end_date": date.today() - timedelta(days=180),
                "status": TreatmentStatus.COMPLETED,
                "notes": "Résection tumorale frontale gauche réussie. Récupération post-opératoire normale."
            },
            {
                "treatment_type": "Radiothérapie",
                "medication_name": None,
                "dosage": "60 Gy en 30 fractions",
                "frequency": "5 séances par semaine",
                "duration": "6 semaines",
                "start_date": date.today() - timedelta(days=150),
                "end_date": date.today() - timedelta(days=108),
                "status": TreatmentStatus.COMPLETED,
                "notes": "Radiothérapie conformationnelle post-chirurgicale. Excellente tolérance."
            },
            {
                "treatment_type": "Chimiothérapie",
                "medication_name": "Temozolomide",
                "dosage": "150 mg/m²",
                "frequency": "1 fois par jour, 5 jours/28 jours",
                "duration": "6 cycles",
                "start_date": date.today() - timedelta(days=90),
                "end_date": date.today() + timedelta(days=60),
                "status": TreatmentStatus.ACTIVE,
                "notes": "Chimiothérapie adjuvante. Cycle 4/6 en cours. Bonne tolérance."
            },
            {
                "treatment_type": "Traitement symptomatique",
                "medication_name": "Dexaméthasone",
                "dosage": "4 mg",
                "frequency": "2 fois par jour",
                "duration": "En continu",
                "start_date": date.today() - timedelta(days=180),
                "end_date": None,
                "status": TreatmentStatus.ACTIVE,
                "notes": "Anti-œdémateux cérébral. Réduction progressive selon évolution."
            },
            {
                "treatment_type": "Traitement symptomatique",
                "medication_name": "Lévétiracétam",
                "dosage": "500 mg",
                "frequency": "2 fois par jour",
                "duration": "6 mois minimum",
                "start_date": date.today() - timedelta(days=180),
                "end_date": date.today() + timedelta(days=90),
                "status": TreatmentStatus.ACTIVE,
                "notes": "Antiépileptique prophylactique post-chirurgie."
            }
        ]
        
        print(f"\n💊 Création de {len(treatments_data)} traitements pour Matheus...")
        
        for treatment_data in treatments_data:
            treatment = Treatment(
                id=str(uuid.uuid4()),
                patient_id=matheus.id,
                prescribed_by_doctor_id=tbib_info.doctor_id,
                **treatment_data,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(treatment)
        
        await session.commit()
        print(f"✅ Traitements créés pour Matheus")
        
        # 4. Créer des segmentations
        print(f"\n🧠 Création de segmentations pour Matheus...")
        
        segmentations_data = [
            {
                "status": SegmentationStatus.COMPLETED,
                "created_at": datetime.now() - timedelta(days=200),
                "notes": "IRM pré-opératoire - Tumeur frontale gauche",
                "results": {
                    "total_tumor_volume_cm3": 45.2,
                    "tumor_analysis": {
                        "tumor_segments": [
                            {"type": "ENHANCING_TUMOR", "volume_cm3": 32.1},
                            {"type": "NECROTIC_CORE", "volume_cm3": 8.5},
                            {"type": "PERITUMORAL_EDEMA", "volume_cm3": 4.6}
                        ]
                    }
                }
            },
            {
                "status": SegmentationStatus.COMPLETED,
                "created_at": datetime.now() - timedelta(days=100),
                "notes": "IRM post-radiothérapie - Contrôle",
                "results": {
                    "total_tumor_volume_cm3": 12.8,
                    "tumor_analysis": {
                        "tumor_segments": [
                            {"type": "ENHANCING_TUMOR", "volume_cm3": 8.2},
                            {"type": "NECROTIC_CORE", "volume_cm3": 3.1},
                            {"type": "PERITUMORAL_EDEMA", "volume_cm3": 1.5}
                        ]
                    }
                }
            },
            {
                "status": SegmentationStatus.COMPLETED,
                "created_at": datetime.now() - timedelta(days=30),
                "notes": "IRM de suivi - Cycle 3 chimiothérapie",
                "results": {
                    "total_tumor_volume_cm3": 8.4,
                    "tumor_analysis": {
                        "tumor_segments": [
                            {"type": "ENHANCING_TUMOR", "volume_cm3": 5.1},
                            {"type": "NECROTIC_CORE", "volume_cm3": 2.3},
                            {"type": "PERITUMORAL_EDEMA", "volume_cm3": 1.0}
                        ]
                    }
                }
            }
        ]
        
        for seg_data in segmentations_data:
            segmentation = AISegmentation(
                id=str(uuid.uuid4()),
                patient_id=matheus.id,
                status=seg_data["status"],
                segmentation_results=seg_data["results"],
                notes=seg_data["notes"],
                created_at=seg_data["created_at"],
                updated_at=seg_data["created_at"]
            )
            session.add(segmentation)
        
        await session.commit()
        print(f"✅ Segmentations créées pour Matheus")
        
        # 5. Résumé
        print(f"\n📊 === RÉSUMÉ DONNÉES MATHEUS CUNHA ===")
        print(f"👤 Patient: Matheus Cunha (ID: {matheus.id[:8]}...)")
        print(f"👨‍⚕️ Médecin assigné: tbib (ID: {tbib_info.doctor_id[:8]}...)")
        print(f"💊 Traitements: {len(treatments_data)} créés")
        print(f"   - 2 terminés (Chirurgie, Radiothérapie)")
        print(f"   - 3 actifs (Chimiothérapie, Dexaméthasone, Lévétiracétam)")
        print(f"🧠 Segmentations: {len(segmentations_data)} créées")
        print(f"   - Évolution: 45.2 → 12.8 → 8.4 cm³ (excellente réponse)")
        
        return matheus.id

async def main():
    """Test principal"""
    
    matheus_id = await create_matheus_complete_data()
    
    print(f"\n🎯 === FLUX DE TEST RECOMMANDÉ ===")
    print(f"1. Connectez-vous avec: tbib@gmail.com / tbib")
    print(f"2. Allez sur le patient Matheus Cunha")
    print(f"3. Testez Treatment Tracking:")
    print(f"   - Plan: 3 traitements actifs")
    print(f"   - History: 2 traitements terminés")
    print(f"   - Ajout nouveau traitement")
    print(f"4. Testez les segmentations:")
    print(f"   - 3 segmentations avec évolution positive")
    print(f"   - Volumes en diminution")

if __name__ == "__main__":
    asyncio.run(main())
