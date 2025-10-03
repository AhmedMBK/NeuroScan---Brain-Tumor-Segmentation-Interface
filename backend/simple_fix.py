#!/usr/bin/env python3
"""
🔧 Correction simple du problème de colonnes manquantes
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from config.database import get_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_columns():
    """Supprime les colonnes problématiques"""
    async for db in get_database():
        try:
            print("🔧 Suppression des colonnes problématiques...")
            
            # Supprimer progress_percentage si elle existe
            try:
                await db.execute(text("""
                    ALTER TABLE ai_segmentations 
                    DROP COLUMN IF EXISTS progress_percentage;
                """))
                print("✅ Colonne progress_percentage supprimée")
            except Exception as e:
                print(f"⚠️ progress_percentage: {e}")
            
            # Supprimer current_step si elle existe
            try:
                await db.execute(text("""
                    ALTER TABLE ai_segmentations 
                    DROP COLUMN IF EXISTS current_step;
                """))
                print("✅ Colonne current_step supprimée")
            except Exception as e:
                print(f"⚠️ current_step: {e}")
            
            await db.commit()
            print("✅ Corrections appliquées")
            
            # Test d'insertion
            print("🧪 Test d'insertion...")
            from models.database_models import AISegmentation, SegmentationStatus
            from datetime import datetime
            import uuid
            
            test_id = str(uuid.uuid4())
            test_segmentation = AISegmentation(
                id=test_id,
                patient_id="test-patient-id",
                doctor_id=None,
                image_series_id="test-series-id",
                status=SegmentationStatus.PROCESSING,
                input_parameters={"test": True},
                started_at=datetime.now()
            )
            
            db.add(test_segmentation)
            await db.flush()
            
            # Supprimer le test
            await db.delete(test_segmentation)
            await db.commit()
            
            print("✅ Test d'insertion réussi!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            await db.rollback()
            return False

async def main():
    print("🔧 CORRECTION SIMPLE DES COLONNES")
    print("=" * 40)
    
    success = await fix_columns()
    
    if success:
        print("\n✅ CORRECTION TERMINÉE!")
        print("🚀 Vous pouvez relancer l'application")
    else:
        print("\n❌ CORRECTION ÉCHOUÉE")

if __name__ == "__main__":
    asyncio.run(main())
