#!/usr/bin/env python3
"""
🔧 Corriger les segmentations orphelines - Assigner un doctor_id
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from models.database_models import AISegmentation, Doctor, User, Patient
from config.settings import Settings

settings = Settings()

async def fix_orphan_segmentations():
    """Assigner les segmentations orphelines au médecin par défaut"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🔧 === CORRECTION SEGMENTATIONS ORPHELINES ===")
        
        # 1. Trouver le médecin par défaut (tbib@gmail.com)
        result = await session.execute(
            select(Doctor.id, User.email)
            .join(User, Doctor.user_id == User.id)
            .where(User.email == "tbib@gmail.com")
        )
        default_doctor = result.first()
        
        if not default_doctor:
            print("❌ Médecin par défaut (tbib@gmail.com) non trouvé")
            return
        
        doctor_id = default_doctor.id
        print(f"✅ Médecin par défaut trouvé: {default_doctor.email} (ID: {doctor_id})")
        
        # 2. Trouver les segmentations orphelines
        result = await session.execute(
            select(AISegmentation.id, AISegmentation.patient_id, AISegmentation.status)
            .where(AISegmentation.doctor_id.is_(None))
        )
        orphan_segmentations = result.all()
        
        if not orphan_segmentations:
            print("✅ Aucune segmentation orpheline trouvée")
            return
        
        print(f"🔍 {len(orphan_segmentations)} segmentations orphelines trouvées:")
        for seg in orphan_segmentations:
            print(f"   - {seg.id[:8]}... | Patient: {seg.patient_id[:8]}... | Status: {seg.status}")
        
        # 3. Assigner le doctor_id aux segmentations orphelines
        result = await session.execute(
            update(AISegmentation)
            .where(AISegmentation.doctor_id.is_(None))
            .values(doctor_id=doctor_id)
        )
        
        await session.commit()
        
        print(f"✅ {result.rowcount} segmentations mises à jour avec doctor_id: {doctor_id}")
        
        # 4. Vérification finale
        result = await session.execute(
            select(AISegmentation.status, AISegmentation.id)
            .where(AISegmentation.doctor_id == doctor_id)
        )
        updated_segmentations = result.all()
        
        print(f"\n📊 Segmentations du Dr. tbib@gmail.com après correction:")
        status_counts = {}
        for seg in updated_segmentations:
            status = str(seg.status).replace('SegmentationStatus.', '')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            print(f"   - {status}: {count}")
        
        print(f"\n🎯 Total: {len(updated_segmentations)} segmentations")

if __name__ == "__main__":
    asyncio.run(fix_orphan_segmentations())
