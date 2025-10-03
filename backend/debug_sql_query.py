#!/usr/bin/env python3
"""
🔍 Debug de la requête SQL pour les statistiques de segmentation
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, case
from models.database_models import User, Doctor, Patient, AISegmentation, SegmentationStatus
from config.settings import Settings

settings = Settings()

async def debug_sql_query():
    """Debug de la requête SQL pour les statistiques"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=True)  # echo=True pour voir les requêtes SQL
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🔍 === DEBUG REQUÊTE SQL STATISTIQUES ===")
        
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
        
        # 2. Test de l'ancienne requête (directe par doctor_id)
        print(f"\n🧪 TEST ANCIENNE REQUÊTE (directe par doctor_id):")
        old_query = select(
            func.count(AISegmentation.id).label("total"),
            func.count(case((AISegmentation.status == SegmentationStatus.COMPLETED, 1))).label("completed"),
            func.count(case((AISegmentation.status == SegmentationStatus.VALIDATED, 1))).label("validated"),
            func.count(case((AISegmentation.status == SegmentationStatus.PROCESSING, 1))).label("processing"),
            func.count(case((AISegmentation.status == SegmentationStatus.FAILED, 1))).label("failed")
        ).where(AISegmentation.doctor_id == tbib_info.doctor_id)
        
        old_result = await session.execute(old_query)
        old_stats = old_result.first()
        
        print(f"   - Total: {old_stats.total}")
        print(f"   - Completed: {old_stats.completed}")
        print(f"   - Validated: {old_stats.validated}")
        
        # 3. Test de la nouvelle requête (via patients assignés)
        print(f"\n🧪 TEST NOUVELLE REQUÊTE (via patients assignés):")
        new_query = select(
            func.count(AISegmentation.id).label("total"),
            func.count(case((AISegmentation.status == SegmentationStatus.COMPLETED, 1))).label("completed"),
            func.count(case((AISegmentation.status == SegmentationStatus.VALIDATED, 1))).label("validated"),
            func.count(case((AISegmentation.status == SegmentationStatus.PROCESSING, 1))).label("processing"),
            func.count(case((AISegmentation.status == SegmentationStatus.FAILED, 1))).label("failed")
        ).join(Patient, AISegmentation.patient_id == Patient.id).where(
            Patient.assigned_doctor_id == tbib_info.doctor_id
        )
        
        new_result = await session.execute(new_query)
        new_stats = new_result.first()
        
        print(f"   - Total: {new_stats.total}")
        print(f"   - Completed: {new_stats.completed}")
        print(f"   - Validated: {new_stats.validated}")
        
        # 4. Vérification détaillée des données
        print(f"\n🔍 VÉRIFICATION DÉTAILLÉE:")
        
        # Compter les segmentations avec doctor_id = tbib
        direct_count = await session.execute(
            select(func.count(AISegmentation.id))
            .where(AISegmentation.doctor_id == tbib_info.doctor_id)
        )
        print(f"   - Segmentations avec doctor_id = tbib: {direct_count.scalar()}")
        
        # Compter les patients assignés à tbib
        patients_count = await session.execute(
            select(func.count(Patient.id))
            .where(Patient.assigned_doctor_id == tbib_info.doctor_id)
        )
        print(f"   - Patients assignés à tbib: {patients_count.scalar()}")
        
        # Compter les segmentations via patients assignés
        via_patients_count = await session.execute(
            select(func.count(AISegmentation.id))
            .join(Patient, AISegmentation.patient_id == Patient.id)
            .where(Patient.assigned_doctor_id == tbib_info.doctor_id)
        )
        print(f"   - Segmentations via patients assignés: {via_patients_count.scalar()}")
        
        # 5. Lister les segmentations détaillées
        print(f"\n📋 LISTE DES SEGMENTATIONS VIA PATIENTS ASSIGNÉS:")
        detailed_query = select(
            AISegmentation.id,
            AISegmentation.status,
            Patient.first_name,
            Patient.last_name,
            Patient.assigned_doctor_id
        ).join(Patient, AISegmentation.patient_id == Patient.id).where(
            Patient.assigned_doctor_id == tbib_info.doctor_id
        )
        
        detailed_result = await session.execute(detailed_query)
        segmentations = detailed_result.all()
        
        for seg in segmentations:
            print(f"   - {seg.id[:8]}... | {seg.status} | {seg.first_name} {seg.last_name}")

if __name__ == "__main__":
    asyncio.run(debug_sql_query())
