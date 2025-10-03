#!/usr/bin/env python3
"""
🔧 Créer le profil médecin manquant pour tbib
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.database_models import User, Doctor, AISegmentation
from config.settings import Settings

settings = Settings()

async def fix_tbib_doctor_profile():
    """Créer le profil médecin manquant pour tbib"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🔧 === CORRECTION PROFIL MÉDECIN TBIB ===")
        
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
        
        # 2. Vérifier s'il a déjà un profil médecin
        result = await session.execute(
            select(Doctor.id, Doctor.user_id)
            .where(Doctor.user_id == user.id)
        )
        existing_doctor = result.first()
        
        if existing_doctor:
            print(f"✅ Profil médecin déjà existant: {existing_doctor.id}")
            return existing_doctor.id
        
        # 3. Trouver le doctor_id utilisé dans les segmentations
        result = await session.execute(
            select(AISegmentation.doctor_id)
            .where(AISegmentation.doctor_id.isnot(None))
            .limit(1)
        )
        existing_doctor_id = result.scalar_one_or_none()
        
        if not existing_doctor_id:
            print("❌ Aucun doctor_id trouvé dans les segmentations")
            return
        
        print(f"🔍 Doctor ID trouvé dans les segmentations: {existing_doctor_id}")
        
        # 4. Vérifier si ce doctor_id existe déjà dans la table doctors
        result = await session.execute(
            select(Doctor.id, Doctor.user_id)
            .where(Doctor.id == existing_doctor_id)
        )
        existing_doctor_record = result.first()
        
        if existing_doctor_record:
            print(f"✅ Profil médecin existe déjà avec ID: {existing_doctor_id}")
            print(f"   - User ID associé: {existing_doctor_record.user_id}")
            
            # Si le profil existe mais n'est pas lié à tbib, le lier
            if existing_doctor_record.user_id != user.id:
                print(f"🔧 Mise à jour du profil médecin pour lier à tbib...")
                await session.execute(
                    f"UPDATE doctors SET user_id = '{user.id}' WHERE id = '{existing_doctor_id}'"
                )
                await session.commit()
                print(f"✅ Profil médecin {existing_doctor_id} maintenant lié à tbib")
            
            return existing_doctor_id
        
        # 5. Créer un nouveau profil médecin avec l'ID existant
        print(f"🔧 Création du profil médecin avec ID: {existing_doctor_id}")
        
        new_doctor = Doctor(
            id=existing_doctor_id,
            user_id=user.id,
            bio="Médecin spécialisé en neurochirurgie et imagerie médicale",
            office_location="Service de Neurochirurgie"
        )
        
        session.add(new_doctor)
        await session.commit()
        
        print(f"✅ Profil médecin créé avec succès:")
        print(f"   - Doctor ID: {existing_doctor_id}")
        print(f"   - User ID: {user.id}")
        print(f"   - Email: {user.email}")
        
        # 6. Vérification finale
        result = await session.execute(
            select(AISegmentation.id, AISegmentation.status)
            .where(AISegmentation.doctor_id == existing_doctor_id)
        )
        segmentations = result.all()
        
        print(f"\n📊 Segmentations maintenant accessibles:")
        status_counts = {}
        for seg in segmentations:
            status = str(seg.status).replace('SegmentationStatus.', '')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            print(f"   - {status}: {count}")
        
        print(f"\n🎯 Total: {len(segmentations)} segmentations")
        
        return existing_doctor_id

if __name__ == "__main__":
    asyncio.run(fix_tbib_doctor_profile())
