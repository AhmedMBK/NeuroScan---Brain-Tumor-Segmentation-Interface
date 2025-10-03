#!/usr/bin/env python3
"""
🔍 Vérifier la relation patient-médecin pour les segmentations
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.database_models import User, Doctor, Patient, AISegmentation
from config.settings import Settings

settings = Settings()

async def verify_patient_doctor_relation():
    """Vérifier la relation patient-médecin pour les segmentations de tbib"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🔍 === VÉRIFICATION RELATION PATIENT-MÉDECIN ===")
        
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
        
        print(f"✅ tbib trouvé:")
        print(f"   - User ID: {tbib_info.id}")
        print(f"   - Doctor ID: {tbib_info.doctor_id}")
        
        # 2. Vérifier les segmentations et leurs patients
        result = await session.execute(
            select(
                AISegmentation.id.label("seg_id"),
                AISegmentation.patient_id,
                AISegmentation.doctor_id.label("seg_doctor_id"),
                AISegmentation.status,
                Patient.first_name,
                Patient.last_name,
                Patient.assigned_doctor_id
            )
            .join(Patient, AISegmentation.patient_id == Patient.id)
            .order_by(AISegmentation.started_at.desc())
        )
        segmentations = result.all()
        
        print(f"\n📊 Analyse des segmentations:")
        print(f"Total segmentations: {len(segmentations)}")
        
        tbib_segmentations_direct = 0
        tbib_segmentations_via_patient = 0
        
        for seg in segmentations:
            print(f"\n🔍 Segmentation {seg.seg_id[:8]}...")
            print(f"   - Patient: {seg.first_name} {seg.last_name} (ID: {seg.patient_id[:8]}...)")
            print(f"   - Status: {seg.status}")
            print(f"   - Segmentation.doctor_id: {seg.seg_doctor_id}")
            print(f"   - Patient.assigned_doctor_id: {seg.assigned_doctor_id}")
            
            # Vérifier si cette segmentation appartient à tbib
            if seg.seg_doctor_id == tbib_info.doctor_id:
                tbib_segmentations_direct += 1
                print(f"   ✅ Appartient à tbib (relation directe)")
            
            if seg.assigned_doctor_id == tbib_info.doctor_id:
                tbib_segmentations_via_patient += 1
                print(f"   ✅ Appartient à tbib (via patient assigné)")
            
            if seg.seg_doctor_id != seg.assigned_doctor_id:
                print(f"   ⚠️ INCOHÉRENCE: doctor_id différent de assigned_doctor_id")
        
        print(f"\n📈 RÉSUMÉ POUR TBIB:")
        print(f"   - Segmentations via relation directe (doctor_id): {tbib_segmentations_direct}")
        print(f"   - Segmentations via patients assignés: {tbib_segmentations_via_patient}")
        
        # 3. Test de la nouvelle requête
        print(f"\n🧪 TEST NOUVELLE REQUÊTE (comme endpoint patients):")
        result = await session.execute(
            select(AISegmentation.id, AISegmentation.status)
            .join(Patient, AISegmentation.patient_id == Patient.id)
            .where(Patient.assigned_doctor_id == tbib_info.doctor_id)
        )
        new_query_results = result.all()
        
        print(f"   - Segmentations trouvées avec nouvelle requête: {len(new_query_results)}")
        
        status_counts = {}
        for seg in new_query_results:
            status = str(seg.status).replace('SegmentationStatus.', '')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            print(f"     * {status}: {count}")

if __name__ == "__main__":
    asyncio.run(verify_patient_doctor_relation())
