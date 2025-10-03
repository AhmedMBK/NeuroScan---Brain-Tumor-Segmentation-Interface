#!/usr/bin/env python3
"""
🔍 Vérifier la structure réelle de la base de données
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from models.database_models import User, Doctor, Patient, AISegmentation
from config.settings import Settings

settings = Settings()

async def check_db_structure():
    """Vérifier la structure réelle de la base"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🔍 === VÉRIFICATION STRUCTURE DB ===")
        
        # 1. Vérifier le type de la colonne status
        print(f"\n📋 STRUCTURE COLONNE STATUS:")
        result = await session.execute(text("""
            SELECT column_name, data_type, udt_name 
            FROM information_schema.columns 
            WHERE table_name = 'ai_segmentations' 
            AND column_name = 'status'
        """))
        column_info = result.first()
        
        if column_info:
            print(f"   - Column: {column_info.column_name}")
            print(f"   - Data type: {column_info.data_type}")
            print(f"   - UDT name: {column_info.udt_name}")
        
        # 2. Vérifier les valeurs enum possibles
        print(f"\n📋 VALEURS ENUM POSSIBLES:")
        try:
            result = await session.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid 
                    FROM pg_type 
                    WHERE typname = 'segmentationstatus'
                )
                ORDER BY enumsortorder
            """))
            enum_values = result.all()
            
            for enum_val in enum_values:
                print(f"   - '{enum_val.enumlabel}'")
        except Exception as e:
            print(f"   ❌ Erreur enum: {e}")
        
        # 3. Vérifier les valeurs réelles dans la table
        print(f"\n📋 VALEURS RÉELLES EN TABLE:")
        try:
            result = await session.execute(text("""
                SELECT status::text, COUNT(*) 
                FROM ai_segmentations 
                GROUP BY status::text
                ORDER BY COUNT(*) DESC
            """))
            real_values = result.all()
            
            for val in real_values:
                print(f"   - '{val[0]}': {val[1]} occurrences")
        except Exception as e:
            print(f"   ❌ Erreur valeurs: {e}")
        
        # 4. Test de requête simple avec cast
        print(f"\n🧪 TEST REQUÊTE AVEC CAST:")
        try:
            result = await session.execute(text("""
                SELECT COUNT(*) 
                FROM ai_segmentations 
                WHERE status::text = 'COMPLETED'
            """))
            count = result.scalar()
            print(f"   ✅ Segmentations COMPLETED: {count}")
        except Exception as e:
            print(f"   ❌ Erreur cast: {e}")
        
        # 5. Test avec jointure patient
        print(f"\n🧪 TEST AVEC JOINTURE PATIENT:")
        try:
            # Trouver tbib
            result = await session.execute(
                select(Doctor.id)
                .join(User, Doctor.user_id == User.id)
                .where(User.email == "tbib@gmail.com")
            )
            doctor_id = result.scalar()
            
            if doctor_id:
                result = await session.execute(text("""
                    SELECT COUNT(*) 
                    FROM ai_segmentations s
                    JOIN patients p ON s.patient_id = p.id
                    WHERE p.assigned_doctor_id = :doctor_id
                    AND s.status::text = 'COMPLETED'
                """), {"doctor_id": doctor_id})
                count = result.scalar()
                print(f"   ✅ Segmentations COMPLETED pour tbib: {count}")
            else:
                print(f"   ❌ tbib non trouvé")
        except Exception as e:
            print(f"   ❌ Erreur jointure: {e}")

if __name__ == "__main__":
    asyncio.run(check_db_structure())
