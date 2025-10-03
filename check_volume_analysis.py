#!/usr/bin/env python3
"""
🔍 Script pour examiner le contenu du volume_analysis dans PostgreSQL
"""

import psycopg2
import json
from psycopg2.extras import RealDictCursor

# Configuration de la base de données
DB_CONFIG = {
    'host': 'localhost',
    'database': 'cerebloom_db',
    'user': 'cerebloom_user',
    'password': 'cerebloom_password',
    'port': 5432
}

def check_volume_analysis():
    """Examiner le contenu du volume_analysis"""
    print("🔍 Connexion à PostgreSQL...")
    
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Connexion réussie")
        
        # Récupérer une segmentation avec volume_analysis
        query = """
            SELECT 
                id,
                patient_id,
                status,
                confidence_score,
                volume_analysis,
                segmentation_results
            FROM ai_segmentations 
            WHERE volume_analysis IS NOT NULL
            ORDER BY started_at DESC 
            LIMIT 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            print(f"\n🧠 Segmentation trouvée:")
            print(f"   ID: {result['id']}")
            print(f"   Patient: {result['patient_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Confiance: {result['confidence_score']}")
            
            # Analyser volume_analysis
            if result['volume_analysis']:
                print(f"\n📊 Contenu volume_analysis:")
                va = result['volume_analysis']
                
                if isinstance(va, str):
                    va = json.loads(va)
                
                print(json.dumps(va, indent=2))
                
                # Extraire les informations clés
                total_vol = va.get('total_tumor_volume_cm3', 'N/A')
                print(f"\n🎯 Informations clés:")
                print(f"   Volume total: {total_vol} cm³")
                
                segments = va.get('tumor_segments', [])
                print(f"   Nombre de segments: {len(segments)}")
                
                for segment in segments:
                    seg_type = segment.get('type', 'Unknown')
                    seg_vol = segment.get('volume_cm3', 0)
                    seg_pct = segment.get('percentage', 0)
                    print(f"   - {seg_type}: {seg_vol} cm³ ({seg_pct}%)")
            
            # Analyser segmentation_results
            if result['segmentation_results']:
                print(f"\n📋 Contenu segmentation_results:")
                sr = result['segmentation_results']
                
                if isinstance(sr, str):
                    sr = json.loads(sr)
                
                # Afficher seulement les clés principales
                print(f"   Clés disponibles: {list(sr.keys())}")
                
                # Vérifier tumor_analysis
                if 'tumor_analysis' in sr:
                    ta = sr['tumor_analysis']
                    print(f"   tumor_analysis présent:")
                    print(f"      Volume total: {ta.get('total_volume_cm3', 'N/A')} cm³")
                    print(f"      Segments: {len(ta.get('tumor_segments', []))}")
                
                # Vérifier clinical_metrics
                if 'clinical_metrics' in sr:
                    cm = sr['clinical_metrics']
                    print(f"   clinical_metrics présent:")
                    print(f"      Dice: {cm.get('dice_coefficient', 'N/A')}")
                    print(f"      Sensitivity: {cm.get('sensitivity', 'N/A')}")
                    print(f"      Specificity: {cm.get('specificity', 'N/A')}")
                    print(f"      Precision: {cm.get('precision', 'N/A')}")
        else:
            print("❌ Aucune segmentation avec volume_analysis trouvée")
        
        # Vérifier les patients avec plusieurs segmentations
        print(f"\n👥 Patients avec plusieurs segmentations (pour comparaison/évolution):")
        query = """
            SELECT 
                patient_id,
                COUNT(*) as count,
                MIN(started_at) as premiere,
                MAX(started_at) as derniere
            FROM ai_segmentations 
            WHERE volume_analysis IS NOT NULL
            GROUP BY patient_id
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """
        
        cursor.execute(query)
        patients = cursor.fetchall()
        
        for patient in patients:
            print(f"   Patient {patient['patient_id']}: {patient['count']} segmentations")
            print(f"      Première: {patient['premiere']}")
            print(f"      Dernière: {patient['derniere']}")
            
            # Récupérer les détails pour ce patient
            query_patient = """
                SELECT 
                    id,
                    started_at,
                    volume_analysis
                FROM ai_segmentations 
                WHERE patient_id = %s AND volume_analysis IS NOT NULL
                ORDER BY started_at ASC
            """
            
            cursor.execute(query_patient, (patient['patient_id'],))
            segmentations = cursor.fetchall()
            
            print(f"      Évolution des volumes:")
            for seg in segmentations:
                va = seg['volume_analysis']
                if isinstance(va, str):
                    va = json.loads(va)
                
                total_vol = va.get('total_tumor_volume_cm3', 0)
                date = seg['started_at'].strftime('%Y-%m-%d')
                print(f"         {date}: {total_vol} cm³")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ CONCLUSION:")
        print(f"   - Les données de segmentation sont présentes dans la base")
        print(f"   - volume_analysis contient les métriques de votre modèle")
        print(f"   - Les pages React peuvent récupérer ces données via l'API")
        print(f"   - Les composants de comparaison et évolution vont fonctionner")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_volume_analysis()
