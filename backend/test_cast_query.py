#!/usr/bin/env python3
"""
🧪 Test de la requête avec cast
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, case, cast, String
from models.database_models import User, Doctor, Patient, AISegmentation
from config.settings import Settings

settings = Settings()

async def test_cast_query():
    """Test de la requête avec cast"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🧪 === TEST REQUÊTE AVEC CAST ===")
        
        # 1. Trouver tbib
        result = await session.execute(
            select(Doctor.id)
            .join(User, Doctor.user_id == User.id)
            .where(User.email == "tbib@gmail.com")
        )
        doctor_id = result.scalar()
        
        if not doctor_id:
            print("❌ tbib non trouvé")
            return
        
        print(f"✅ tbib trouvé: Doctor ID = {doctor_id}")
        
        # 2. Test de la requête avec cast
        print(f"\n🧪 TEST REQUÊTE AVEC CAST:")
        
        try:
            cast_query = select(
                func.count(AISegmentation.id).label("total"),
                func.count(case((cast(AISegmentation.status, String) == "COMPLETED", 1))).label("completed"),
                func.count(case((cast(AISegmentation.status, String) == "VALIDATED", 1))).label("validated"),
                func.count(case((cast(AISegmentation.status, String) == "PROCESSING", 1))).label("processing"),
                func.count(case((cast(AISegmentation.status, String) == "FAILED", 1))).label("failed")
            ).join(Patient, AISegmentation.patient_id == Patient.id).where(
                Patient.assigned_doctor_id == doctor_id
            )
            
            cast_result = await session.execute(cast_query)
            cast_stats = cast_result.first()
            
            print(f"   ✅ SUCCÈS!")
            print(f"   - Total: {cast_stats.total}")
            print(f"   - Completed: {cast_stats.completed}")
            print(f"   - Validated: {cast_stats.validated}")
            print(f"   - Processing: {cast_stats.processing}")
            print(f"   - Failed: {cast_stats.failed}")
            
        except Exception as e:
            print(f"   ❌ ERREUR: {e}")

if __name__ == "__main__":
    asyncio.run(test_cast_query())
