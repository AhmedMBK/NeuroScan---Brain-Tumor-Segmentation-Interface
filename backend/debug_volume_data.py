#!/usr/bin/env python3
"""
🔍 Debug des données de volume dans segmentation_results
"""

import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.database_models import User, Doctor, Patient, AISegmentation
from config.settings import Settings

settings = Settings()

async def debug_volume_data():
    """Debug des données de volume"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🔍 === DEBUG DONNÉES DE VOLUME ===")
        
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
        
        # 2. Récupérer les segmentations COMPLETED de tbib
        result = await session.execute(
            select(
                AISegmentation.id,
                AISegmentation.segmentation_results,
                AISegmentation.volume_analysis
            )
            .join(Patient, AISegmentation.patient_id == Patient.id)
            .where(Patient.assigned_doctor_id == doctor_id)
            .where(AISegmentation.segmentation_results.isnot(None))
        )
        segmentations = result.all()
        
        print(f"\n📊 SEGMENTATIONS AVEC RÉSULTATS: {len(segmentations)}")
        
        total_volumes = []
        necrotic_volumes = []
        edema_volumes = []
        enhancing_volumes = []
        
        for i, seg in enumerate(segmentations, 1):
            print(f"\n🔍 SEGMENTATION {i} (ID: {seg.id[:8]}...):")
            
            # Analyser segmentation_results
            if seg.segmentation_results:
                print(f"   📋 SEGMENTATION_RESULTS:")
                results = seg.segmentation_results
                
                # Afficher la structure complète
                print(f"   - Clés disponibles: {list(results.keys())}")
                
                # Volume total
                total_vol = results.get("total_tumor_volume_cm3", 0)
                print(f"   - total_tumor_volume_cm3: {total_vol}")
                if total_vol > 0:
                    total_volumes.append(total_vol)
                
                # Volumes par type
                necrotic_data = results.get("volume_necrotic_core", {})
                print(f"   - volume_necrotic_core: {necrotic_data}")
                if isinstance(necrotic_data, dict) and necrotic_data.get("cm3", 0) > 0:
                    necrotic_volumes.append(necrotic_data["cm3"])
                
                edema_data = results.get("volume_peritumoral_edema", {})
                print(f"   - volume_peritumoral_edema: {edema_data}")
                if isinstance(edema_data, dict) and edema_data.get("cm3", 0) > 0:
                    edema_volumes.append(edema_data["cm3"])
                
                enhancing_data = results.get("volume_enhancing_tumor", {})
                print(f"   - volume_enhancing_tumor: {enhancing_data}")
                if isinstance(enhancing_data, dict) and enhancing_data.get("cm3", 0) > 0:
                    enhancing_volumes.append(enhancing_data["cm3"])
                
                # Vérifier tumor_analysis
                tumor_analysis = results.get("tumor_analysis", {})
                if tumor_analysis:
                    print(f"   - tumor_analysis présent: {tumor_analysis}")
            
            # Analyser volume_analysis
            if seg.volume_analysis:
                print(f"   📋 VOLUME_ANALYSIS:")
                print(f"   - {seg.volume_analysis}")
        
        # 3. Calculer les moyennes comme dans l'endpoint
        print(f"\n📈 CALCUL DES MOYENNES:")
        print(f"   - Total volumes trouvés: {total_volumes}")
        print(f"   - Necrotic volumes trouvés: {necrotic_volumes}")
        print(f"   - Edema volumes trouvés: {edema_volumes}")
        print(f"   - Enhancing volumes trouvés: {enhancing_volumes}")
        
        avg_total = sum(total_volumes) / len(total_volumes) if total_volumes else 0
        avg_necrotic = sum(necrotic_volumes) / len(necrotic_volumes) if necrotic_volumes else 0
        avg_edema = sum(edema_volumes) / len(edema_volumes) if edema_volumes else 0
        avg_enhancing = sum(enhancing_volumes) / len(enhancing_volumes) if enhancing_volumes else 0
        
        print(f"\n🎯 MOYENNES CALCULÉES:")
        print(f"   - Total tumor: {avg_total:.2f} cm³")
        print(f"   - Necrotic core: {avg_necrotic:.2f} cm³")
        print(f"   - Peritumoral edema: {avg_edema:.2f} cm³")
        print(f"   - Enhancing tumor: {avg_enhancing:.2f} cm³")

if __name__ == "__main__":
    asyncio.run(debug_volume_data())
