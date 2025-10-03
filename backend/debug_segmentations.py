#!/usr/bin/env python3
"""
🔍 Debug des segmentations - Vérifier les doctor_id
"""

import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from models.database_models import AISegmentation, Doctor, User, Patient
from config.settings import Settings

settings = Settings()

async def debug_segmentations():
    """Vérifier les segmentations et leurs doctor_id"""
    
    # Connexion à la base de données
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🔍 === DEBUG SEGMENTATIONS ===")
        
        # 1. Lister toutes les segmentations
        print("\n1. 📋 Toutes les segmentations:")
        result = await session.execute(
            select(AISegmentation.id, AISegmentation.patient_id, AISegmentation.doctor_id, AISegmentation.status)
            .order_by(AISegmentation.started_at.desc())
        )
        segmentations = result.all()
        
        for seg in segmentations:
            print(f"   - ID: {seg.id[:8]}... | Patient: {seg.patient_id[:8]}... | Doctor: {seg.doctor_id} | Status: {seg.status}")
        
        # 2. Lister tous les médecins
        print("\n2. 👨‍⚕️ Tous les médecins:")
        result = await session.execute(
            select(Doctor.id, Doctor.user_id, User.first_name, User.last_name, User.email)
            .join(User, Doctor.user_id == User.id)
        )
        doctors = result.all()
        
        for doc in doctors:
            print(f"   - Doctor ID: {doc.id} | User: {doc.first_name} {doc.last_name} ({doc.email})")
        
        # 3. Vérifier les segmentations sans doctor_id
        print("\n3. ⚠️ Segmentations sans doctor_id:")
        result = await session.execute(
            select(AISegmentation.id, AISegmentation.patient_id, AISegmentation.status)
            .where(AISegmentation.doctor_id.is_(None))
        )
        orphan_segmentations = result.all()
        
        if orphan_segmentations:
            print(f"   ❌ {len(orphan_segmentations)} segmentations sans doctor_id trouvées:")
            for seg in orphan_segmentations:
                print(f"      - ID: {seg.id[:8]}... | Patient: {seg.patient_id[:8]}... | Status: {seg.status}")
        else:
            print("   ✅ Toutes les segmentations ont un doctor_id")
        
        # 4. Vérifier les patients et leurs médecins assignés
        print("\n4. 🏥 Patients et médecins assignés:")
        result = await session.execute(
            select(Patient.id, Patient.first_name, Patient.last_name, Patient.assigned_doctor_id)
            .order_by(Patient.created_at.desc())
            .limit(5)
        )
        patients = result.all()
        
        for patient in patients:
            print(f"   - Patient: {patient.first_name} {patient.last_name} | Assigned Doctor: {patient.assigned_doctor_id}")
        
        # 5. Statistiques par médecin
        print("\n5. 📊 Statistiques par médecin:")
        for doc in doctors:
            result = await session.execute(
                select(AISegmentation.status, text("COUNT(*)"))
                .where(AISegmentation.doctor_id == doc.id)
                .group_by(AISegmentation.status)
            )
            stats = result.all()
            
            if stats:
                print(f"   - Dr. {doc.first_name} {doc.last_name}:")
                for status, count in stats:
                    print(f"     * {status}: {count}")
            else:
                print(f"   - Dr. {doc.first_name} {doc.last_name}: Aucune segmentation")

if __name__ == "__main__":
    asyncio.run(debug_segmentations())
