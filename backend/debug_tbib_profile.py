#!/usr/bin/env python3
"""
🔍 Debug du profil médecin de tbib
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.database_models import User, Doctor, AISegmentation
from config.settings import Settings

settings = Settings()

async def debug_tbib_profile():
    """Vérifier le profil médecin de tbib"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🔍 === DEBUG PROFIL TBIB ===")
        
        # 1. Trouver l'utilisateur tbib
        result = await session.execute(
            select(User.id, User.email, User.first_name, User.last_name, User.role)
            .where(User.email == "tbib@gmail.com")
        )
        user = result.first()
        
        if not user:
            print("❌ Utilisateur tbib@gmail.com non trouvé")
            return
        
        print(f"✅ Utilisateur trouvé:")
        print(f"   - ID: {user.id}")
        print(f"   - Email: {user.email}")
        print(f"   - Nom: {user.first_name} {user.last_name}")
        print(f"   - Rôle: {user.role}")
        
        # 2. Chercher le profil médecin associé
        result = await session.execute(
            select(Doctor.id, Doctor.user_id, Doctor.bio, Doctor.office_location)
            .where(Doctor.user_id == user.id)
        )
        doctor = result.first()

        if not doctor:
            print("❌ PROBLÈME: Aucun profil médecin trouvé pour cet utilisateur")
            print("   C'est pourquoi les statistiques retournent 0 !")
            return

        print(f"✅ Profil médecin trouvé:")
        print(f"   - Doctor ID: {doctor.id}")
        print(f"   - User ID: {doctor.user_id}")
        print(f"   - Bio: {doctor.bio}")
        print(f"   - Bureau: {doctor.office_location}")
        
        # 3. Vérifier les segmentations avec ce doctor_id
        result = await session.execute(
            select(AISegmentation.id, AISegmentation.status, AISegmentation.patient_id)
            .where(AISegmentation.doctor_id == doctor.id)
        )
        segmentations = result.all()
        
        print(f"\n📊 Segmentations avec doctor_id = {doctor.id}:")
        if segmentations:
            for seg in segmentations:
                print(f"   - {seg.id[:8]}... | Status: {seg.status} | Patient: {seg.patient_id[:8]}...")
            print(f"   Total: {len(segmentations)}")
        else:
            print("   ❌ Aucune segmentation trouvée avec ce doctor_id")
        
        # 4. Vérifier toutes les segmentations dans la DB
        result = await session.execute(
            select(AISegmentation.id, AISegmentation.doctor_id, AISegmentation.status)
        )
        all_segmentations = result.all()
        
        print(f"\n📋 Toutes les segmentations dans la DB:")
        for seg in all_segmentations:
            doctor_match = "✅" if seg.doctor_id == doctor.id else "❌"
            print(f"   {doctor_match} {seg.id[:8]}... | Doctor: {seg.doctor_id} | Status: {seg.status}")

if __name__ == "__main__":
    asyncio.run(debug_tbib_profile())
