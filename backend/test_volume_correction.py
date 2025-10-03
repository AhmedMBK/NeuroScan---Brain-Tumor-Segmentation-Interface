#!/usr/bin/env python3
"""
🧪 Test de la correction des volumes
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, cast, String
from models.database_models import User, Doctor, Patient, AISegmentation
from config.settings import Settings

settings = Settings()

async def test_volume_correction():
    """Test de la correction des volumes"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🧪 === TEST CORRECTION VOLUMES ===")
        
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
        
        # 2. Récupérer les segmentations COMPLETED avec la nouvelle logique
        completed_query = select(AISegmentation.segmentation_results).where(
            cast(AISegmentation.status, String) == "COMPLETED"
        ).where(AISegmentation.segmentation_results.isnot(None)).join(
            Patient, AISegmentation.patient_id == Patient.id
        ).where(Patient.assigned_doctor_id == doctor_id)
        
        completed_segmentations = await session.execute(completed_query)
        
        # 3. Appliquer la nouvelle logique d'extraction
        total_volumes = []
        necrotic_volumes = []
        edema_volumes = []
        enhancing_volumes = []
        
        for result in completed_segmentations.scalars():
            if result and isinstance(result, dict):
                # Extraire le volume total
                total_vol = result.get("total_tumor_volume_cm3", 0)
                if total_vol > 0:
                    total_volumes.append(total_vol)

                # NOUVELLE LOGIQUE: Extraire les volumes depuis tumor_analysis
                tumor_analysis = result.get("tumor_analysis", {})
                tumor_segments = tumor_analysis.get("tumor_segments", [])
                
                print(f"🔍 Segmentation avec {len(tumor_segments)} segments:")
                
                for segment in tumor_segments:
                    segment_type = segment.get("type", "")
                    volume_cm3 = segment.get("volume_cm3", 0)
                    
                    print(f"   - {segment_type}: {volume_cm3} cm³")
                    
                    if volume_cm3 > 0:
                        if segment_type == "NECROTIC_CORE":
                            necrotic_volumes.append(volume_cm3)
                        elif segment_type == "PERITUMORAL_EDEMA":
                            edema_volumes.append(volume_cm3)
                        elif segment_type == "ENHANCING_TUMOR":
                            enhancing_volumes.append(volume_cm3)
        
        # 4. Calculer les moyennes
        avg_total = sum(total_volumes) / len(total_volumes) if total_volumes else 0
        avg_necrotic = sum(necrotic_volumes) / len(necrotic_volumes) if necrotic_volumes else 0
        avg_edema = sum(edema_volumes) / len(edema_volumes) if edema_volumes else 0
        avg_enhancing = sum(enhancing_volumes) / len(enhancing_volumes) if enhancing_volumes else 0
        
        print(f"\n📈 RÉSULTATS AVEC NOUVELLE LOGIQUE:")
        print(f"   - Total volumes: {total_volumes}")
        print(f"   - Necrotic volumes: {necrotic_volumes}")
        print(f"   - Edema volumes: {edema_volumes}")
        print(f"   - Enhancing volumes: {enhancing_volumes}")
        
        print(f"\n🎯 MOYENNES CORRIGÉES:")
        print(f"   - Total tumor: {avg_total:.2f} cm³")
        print(f"   - Necrotic core: {avg_necrotic:.2f} cm³")
        print(f"   - Peritumoral edema: {avg_edema:.2f} cm³")
        print(f"   - Enhancing tumor: {avg_enhancing:.2f} cm³")

if __name__ == "__main__":
    asyncio.run(test_volume_correction())
