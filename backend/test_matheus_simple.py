#!/usr/bin/env python3
"""
🧪 Test simple pour vérifier Matheus Cunha
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from models.database_models import Patient, Treatment, AISegmentation, Doctor, User
from config.settings import Settings

async def check_matheus_data():
    """Vérifier les données de Matheus Cunha"""
    
    settings = Settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🔍 === VÉRIFICATION MATHEUS CUNHA ===")
        
        # Chercher Matheus
        result = await session.execute(
            select(Patient).where(
                Patient.first_name.ilike("%matheus%"),
                Patient.last_name.ilike("%cunha%")
            )
        )
        matheus = result.scalar_one_or_none()
        
        if matheus:
            print(f"✅ Matheus trouvé: {matheus.first_name} {matheus.last_name}")
            print(f"   ID: {matheus.id}")
            print(f"   Médecin assigné: {matheus.assigned_doctor_id}")
            
            # Compter ses traitements
            result = await session.execute(
                select(func.count(Treatment.id))
                .where(Treatment.patient_id == matheus.id)
            )
            treatment_count = result.scalar()
            print(f"   Traitements: {treatment_count}")
            
            # Compter ses segmentations
            result = await session.execute(
                select(func.count(AISegmentation.id))
                .where(AISegmentation.patient_id == matheus.id)
            )
            segmentation_count = result.scalar()
            print(f"   Segmentations: {segmentation_count}")
            
            return matheus.id
        else:
            print("❌ Matheus Cunha non trouvé")
            
            # Lister tous les patients
            result = await session.execute(
                select(Patient.first_name, Patient.last_name, Patient.id)
                .limit(10)
            )
            patients = result.all()
            
            print(f"\n📋 Patients disponibles:")
            for p in patients:
                print(f"   - {p.first_name} {p.last_name} (ID: {p.id[:8]}...)")
            
            return None

async def check_tbib():
    """Vérifier tbib"""
    
    settings = Settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print(f"\n🔍 === VÉRIFICATION TBIB ===")
        
        # Chercher tbib
        result = await session.execute(
            select(User.id, User.email, Doctor.id.label("doctor_id"))
            .join(Doctor, Doctor.user_id == User.id, isouter=True)
            .where(User.email == "tbib@gmail.com")
        )
        tbib = result.first()
        
        if tbib:
            print(f"✅ tbib trouvé:")
            print(f"   Email: {tbib.email}")
            print(f"   User ID: {tbib.id}")
            print(f"   Doctor ID: {tbib.doctor_id}")
            
            if tbib.doctor_id:
                # Compter ses patients
                result = await session.execute(
                    select(func.count(Patient.id))
                    .where(Patient.assigned_doctor_id == tbib.doctor_id)
                )
                patient_count = result.scalar()
                print(f"   Patients assignés: {patient_count}")
            
            return tbib.doctor_id
        else:
            print("❌ tbib non trouvé")
            return None

async def main():
    """Test principal"""
    
    # Vérifier tbib
    doctor_id = await check_tbib()
    
    # Vérifier Matheus
    matheus_id = await check_matheus_data()
    
    print(f"\n🎯 === RÉSUMÉ ===")
    if doctor_id and matheus_id:
        print("✅ Prêt pour tester le flux Treatment Tracking")
        print("   1. Connectez-vous avec tbib@gmail.com / tbib")
        print("   2. Allez sur Matheus Cunha")
        print("   3. Testez Treatment Tracking")
    else:
        print("❌ Données manquantes pour le test")

if __name__ == "__main__":
    asyncio.run(main())
