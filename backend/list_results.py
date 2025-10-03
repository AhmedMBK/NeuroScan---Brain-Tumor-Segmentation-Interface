#!/usr/bin/env python3
"""
📁 Listeur de Résultats CereBloom
Script pour afficher tous les résultats de segmentation
"""

import os
from pathlib import Path
from datetime import datetime
import json

def list_segmentation_results():
    """Liste tous les résultats de segmentation"""
    print("📁 RÉSULTATS DE SEGMENTATION CEREBLOOM")
    print("=" * 60)
    
    results_dir = Path("uploads/segmentation_results")
    
    if not results_dir.exists():
        print("❌ Aucun dossier de résultats trouvé")
        return
    
    # Lister tous les dossiers de résultats
    result_folders = [f for f in results_dir.iterdir() if f.is_dir()]
    
    if not result_folders:
        print("📂 Aucun résultat trouvé")
        return
    
    print(f"📊 {len(result_folders)} résultat(s) trouvé(s):\n")
    
    # Trier par date de modification (plus récent en premier)
    result_folders.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for i, folder in enumerate(result_folders, 1):
        print(f"🔬 RÉSULTAT #{i}")
        print(f"📂 Dossier: {folder.name}")
        
        # Date de création
        creation_time = datetime.fromtimestamp(folder.stat().st_mtime)
        print(f"📅 Date: {creation_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Lister les fichiers
        files = list(folder.glob("*"))
        print(f"📄 Fichiers ({len(files)}):")
        
        total_size = 0
        for file in files:
            size_mb = file.stat().st_size / (1024 * 1024)
            total_size += size_mb
            
            # Icône selon le type de fichier
            if file.suffix == '.gz':
                icon = "🧠"
                desc = "Masque de segmentation"
            elif file.suffix == '.json':
                icon = "📊"
                desc = "Métriques"
            elif file.suffix == '.txt':
                icon = "📄"
                desc = "Rapport"
            else:
                icon = "📁"
                desc = "Fichier"
            
            print(f"   {icon} {file.name} ({size_mb:.1f} MB) - {desc}")
        
        print(f"💾 Taille totale: {total_size:.1f} MB")
        
        # Essayer de lire les métriques si disponibles
        metrics_files = list(folder.glob("*metrics*.json"))
        if metrics_files:
            try:
                with open(metrics_files[0], 'r', encoding='utf-8') as f:
                    metrics = json.load(f)
                
                volume = metrics.get('total_tumor_volume_cm3', 'N/A')
                method = metrics.get('processing_info', {}).get('method', 'N/A')
                classes = len(metrics.get('class_details', {}))
                
                print(f"🎯 Volume total: {volume} cm³")
                print(f"🔬 Méthode: {method}")
                print(f"🏷️ Classes trouvées: {classes}")
                
            except Exception as e:
                print(f"⚠️ Erreur lecture métriques: {e}")
        
        print(f"📍 Chemin complet: {folder.absolute()}")
        print("-" * 60)
    
    print(f"\n💡 COMMENT OUVRIR LES FICHIERS:")
    print(f"🧠 Masques .nii.gz → ITK-SNAP, 3D Slicer, FSLeyes")
    print(f"📊 Métriques .json → Éditeur de texte, navigateur web")
    print(f"📄 Rapports .txt → Bloc-notes, éditeur de texte")
    
    print(f"\n📂 DOSSIER PRINCIPAL:")
    print(f"   {results_dir.absolute()}")

if __name__ == "__main__":
    list_segmentation_results()
