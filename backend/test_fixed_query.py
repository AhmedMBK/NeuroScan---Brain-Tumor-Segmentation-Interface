#!/usr/bin/env python3
"""
🧪 Test de la requête corrigée avec .value
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, case
from models.database_models import User, Doctor, Patient, AISegmentation, SegmentationStatus
from config.settings import Settings

settings = Settings()

async def test_fixed_query():
    """Test de la requête corrigée"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🧪 === TEST REQUÊTE CORRIGÉE ===")
        
        # 1. Trouver tbib et son profil médecin
        result = await session.execute(
            select(User.id, User.email, Doctor.id.label("doctor_id"))
            .join(Doctor, Doctor.user_id == User.id)
            .where(User.email == "tbib@gmail.com")
        )
        tbib_info = result.first()
        
        if not tbib_info:
            print("❌ tbib ou son profil médecin non trouvé")
            return
        
        print(f"✅ tbib trouvé: Doctor ID = {tbib_info.doctor_id}")
        
        # 2. Test de la requête corrigée (avec .value)
        print(f"\n🧪 TEST REQUÊTE CORRIGÉE (avec .value):")
        
        try:
            corrected_query = select(
                func.count(AISegmentation.id).label("total"),
                func.count(case((AISegmentation.status == "COMPLETED", 1))).label("completed"),
                func.count(case((AISegmentation.status == "VALIDATED", 1))).label("validated"),
                func.count(case((AISegmentation.status == "PROCESSING", 1))).label("processing"),
                func.count(case((AISegmentation.status == "FAILED", 1))).label("failed")
            ).join(Patient, AISegmentation.patient_id == Patient.id).where(
                Patient.assigned_doctor_id == tbib_info.doctor_id
            )
            
            corrected_result = await session.execute(corrected_query)
            corrected_stats = corrected_result.first()
            
            print(f"   ✅ SUCCÈS!")
            print(f"   - Total: {corrected_stats.total}")
            print(f"   - Completed: {corrected_stats.completed}")
            print(f"   - Validated: {corrected_stats.validated}")
            print(f"   - Processing: {corrected_stats.processing}")
            print(f"   - Failed: {corrected_stats.failed}")
            
            # 3. Vérification des valeurs d'enum
            print(f"\n🔍 VALEURS D'ENUM:")
            print(f"   - COMPLETED.value = '{SegmentationStatus.COMPLETED.value}'")
            print(f"   - VALIDATED.value = '{SegmentationStatus.VALIDATED.value}'")
            print(f"   - PROCESSING.value = '{SegmentationStatus.PROCESSING.value}'")
            print(f"   - FAILED.value = '{SegmentationStatus.FAILED.value}'")
            
            # 4. Vérification des statuts réels en base
            print(f"\n🔍 STATUTS RÉELS EN BASE:")
            status_query = select(
                AISegmentation.status,
                func.count(AISegmentation.id).label("count")
            ).join(Patient, AISegmentation.patient_id == Patient.id).where(
                Patient.assigned_doctor_id == tbib_info.doctor_id
            ).group_by(AISegmentation.status)
            
            status_result = await session.execute(status_query)
            statuses = status_result.all()
            
            for status_row in statuses:
                print(f"   - '{status_row.status}': {status_row.count}")
            
        except Exception as e:
            print(f"   ❌ ERREUR: {e}")

if __name__ == "__main__":
    asyncio.run(test_fixed_query())
