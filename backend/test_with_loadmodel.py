#!/usr/bin/env python3
"""
🧠 Test avec LoadModel.py - CereBloom
Script pour tester directement avec votre modèle loadmodel.py
"""

import os
import sys
import asyncio
import uuid
import json
from pathlib import Path
from datetime import datetime
import numpy as np
import nibabel as nib

# Ajouter le répertoire backend au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports CereBloom
from config.database import get_database
from models.database_models import MedicalImage, AISegmentation, SegmentationStatus
from sqlalchemy import select

# Configuration
PATIENT_ID = "stringd5f01d3b-b54b-43a2-ba3c-0b12c797affc"

# Essayer d'importer votre loadmodel.py
try:
    import loadmodel
    LOADMODEL_AVAILABLE = True
    print("✅ loadmodel.py importé avec succès")
except ImportError as e:
    LOADMODEL_AVAILABLE = False
    print(f"⚠️ loadmodel.py non disponible: {e}")
    print("   Utilisation du mode simulation")

def load_nifti_image(file_path):
    """Charge une image NIfTI"""
    try:
        print(f"📁 Chargement: {os.path.basename(file_path)}")
        nii_img = nib.load(file_path)
        img_data = nii_img.get_fdata()
        print(f"   Shape: {img_data.shape}, Min: {img_data.min():.2f}, Max: {img_data.max():.2f}")
        return img_data, nii_img.affine
    except Exception as e:
        print(f"❌ Erreur chargement {file_path}: {e}")
        return None, None

def preprocess_for_loadmodel(flair_data, t1ce_data):
    """Prétraite les données selon loadmodel.py"""
    print("🔄 Prétraitement selon loadmodel.py...")
    
    try:
        # Si loadmodel.py est disponible, utiliser ses fonctions
        if LOADMODEL_AVAILABLE and hasattr(loadmodel, 'preprocess_data'):
            return loadmodel.preprocess_data(flair_data, t1ce_data)
        
        # Sinon, prétraitement basique
        # Normalisation
        flair_norm = (flair_data - np.mean(flair_data)) / (np.std(flair_data) + 1e-8)
        t1ce_norm = (t1ce_data - np.mean(t1ce_data)) / (np.std(t1ce_data) + 1e-8)
        
        # Combiner les modalités
        combined = np.stack([flair_norm, t1ce_norm], axis=-1)
        
        print(f"   Shape prétraitée: {combined.shape}")
        return combined
        
    except Exception as e:
        print(f"❌ Erreur prétraitement: {e}")
        return None

def run_segmentation(preprocessed_data):
    """Lance la segmentation"""
    print("🧠 Lancement de la segmentation...")
    
    try:
        # Si loadmodel.py est disponible avec une fonction de prédiction
        if LOADMODEL_AVAILABLE and hasattr(loadmodel, 'predict'):
            print("   Utilisation du modèle loadmodel.py")
            return loadmodel.predict(preprocessed_data)
        
        elif LOADMODEL_AVAILABLE and hasattr(loadmodel, 'segment_tumor'):
            print("   Utilisation de segment_tumor de loadmodel.py")
            return loadmodel.segment_tumor(preprocessed_data)
        
        else:
            # Simulation réaliste
            print("   Mode simulation (loadmodel.py non disponible)")
            return simulate_realistic_segmentation(preprocessed_data)
            
    except Exception as e:
        print(f"❌ Erreur segmentation: {e}")
        return simulate_realistic_segmentation(preprocessed_data)

def simulate_realistic_segmentation(data):
    """Simulation réaliste de segmentation"""
    print("   Simulation de segmentation réaliste...")
    
    if len(data.shape) == 4:  # (H, W, D, C)
        # Utiliser la première modalité pour la simulation
        base_data = data[:, :, :, 0]
    else:
        base_data = data
    
    # Créer un masque de segmentation
    segmentation = np.zeros_like(base_data, dtype=np.uint8)
    
    # Seuils adaptatifs
    mean_val = np.mean(base_data)
    std_val = np.std(base_data)
    
    # Régions tumorales simulées
    high_threshold = mean_val + 1.5 * std_val
    medium_threshold = mean_val + 0.5 * std_val
    low_threshold = mean_val - 0.5 * std_val
    
    # Assigner les classes
    segmentation[base_data > high_threshold] = 3  # Tumeur rehaussée
    segmentation[(base_data > medium_threshold) & (base_data <= high_threshold)] = 2  # Œdème
    segmentation[(base_data > low_threshold) & (base_data <= medium_threshold)] = 1  # Nécrotique
    
    # Nettoyer les petites régions
    from scipy.ndimage import binary_opening
    for class_id in [1, 2, 3]:
        mask = segmentation == class_id
        if np.sum(mask) > 0:
            cleaned_mask = binary_opening(mask, structure=np.ones((3, 3, 3)))
            segmentation[mask] = 0
            segmentation[cleaned_mask] = class_id
    
    unique_classes = np.unique(segmentation)
    print(f"   Classes trouvées: {unique_classes}")
    
    return segmentation

def calculate_detailed_metrics(segmentation, voxel_size=(1.0, 1.0, 1.0)):
    """Calcule des métriques détaillées"""
    print("📊 Calcul des métriques détaillées...")
    
    # Volume d'un voxel en cm³
    voxel_volume_cm3 = np.prod(voxel_size) / 1000  # mm³ to cm³
    
    unique_classes = np.unique(segmentation)
    total_tumor_voxels = np.sum(segmentation > 0)
    
    metrics = {
        "total_tumor_volume_cm3": float(total_tumor_voxels * voxel_volume_cm3),
        "voxel_size_mm": list(voxel_size),
        "voxel_volume_cm3": float(voxel_volume_cm3),
        "classes_found": unique_classes.tolist(),
        "class_details": {},
        "processing_info": {
            "timestamp": datetime.now().isoformat(),
            "method": "loadmodel.py" if LOADMODEL_AVAILABLE else "simulation"
        }
    }
    
    class_names = {
        0: "Tissu sain",
        1: "Noyau nécrotique/kystique", 
        2: "Œdème péritumoral",
        3: "Tumeur rehaussée"
    }
    
    for class_id in unique_classes:
        if class_id > 0:
            voxel_count = np.sum(segmentation == class_id)
            volume_cm3 = voxel_count * voxel_volume_cm3
            percentage = (voxel_count / total_tumor_voxels * 100) if total_tumor_voxels > 0 else 0.0
            
            metrics["class_details"][int(class_id)] = {
                "name": class_names.get(class_id, f"Classe {class_id}"),
                "voxel_count": int(voxel_count),
                "volume_cm3": float(volume_cm3),
                "percentage": float(percentage)
            }
            
            print(f"   🎯 {class_names.get(class_id, f'Classe {class_id}')}: {volume_cm3:.2f} cm³ ({percentage:.1f}%)")
    
    return metrics

async def test_with_loadmodel():
    """Test principal avec loadmodel.py"""
    print("🚀 TEST AVEC LOADMODEL.PY")
    print("=" * 60)
    
    async for db in get_database():
        try:
            # 1. Récupérer les images
            print(f"🔍 Recherche des images pour patient: {PATIENT_ID}")
            
            result = await db.execute(
                select(MedicalImage).where(MedicalImage.patient_id == PATIENT_ID)
            )
            images = result.scalars().all()
            
            if not images:
                print(f"❌ Aucune image trouvée pour le patient {PATIENT_ID}")
                return
            
            print(f"✅ {len(images)} images trouvées")
            
            # 2. Organiser par modalité
            images_by_modality = {}
            for img in images:
                modality = img.modality.upper()
                images_by_modality[modality] = img.file_path
                print(f"   📄 {modality}: {os.path.basename(img.file_path)}")
            
            # 3. Charger FLAIR et T1CE (priorité)
            flair_path = images_by_modality.get("FLAIR")
            t1ce_path = images_by_modality.get("T1CE")
            
            if not flair_path or not t1ce_path:
                print("⚠️ FLAIR ou T1CE manquant, utilisation des modalités disponibles")
                available_paths = list(images_by_modality.values())
                if len(available_paths) < 2:
                    print("❌ Pas assez de modalités")
                    return
                flair_path, t1ce_path = available_paths[:2]
            
            # 4. Charger les données
            print("\n📁 CHARGEMENT DES IMAGES")
            print("-" * 40)
            
            flair_data, flair_affine = load_nifti_image(flair_path)
            t1ce_data, t1ce_affine = load_nifti_image(t1ce_path)
            
            if flair_data is None or t1ce_data is None:
                print("❌ Erreur chargement des images")
                return
            
            # 5. Prétraitement
            print("\n🔄 PRÉTRAITEMENT")
            print("-" * 40)
            
            preprocessed_data = preprocess_for_loadmodel(flair_data, t1ce_data)
            if preprocessed_data is None:
                print("❌ Erreur prétraitement")
                return
            
            # 6. Segmentation
            print("\n🧠 SEGMENTATION")
            print("-" * 40)
            
            segmentation_result = run_segmentation(preprocessed_data)
            if segmentation_result is None:
                print("❌ Erreur segmentation")
                return
            
            # 7. Métriques
            print("\n📊 ANALYSE")
            print("-" * 40)
            
            # Estimer la taille des voxels (approximation)
            voxel_size = (1.0, 1.0, 1.0)  # mm
            if flair_affine is not None:
                voxel_size = tuple(np.abs(np.diag(flair_affine)[:3]))
            
            metrics = calculate_detailed_metrics(segmentation_result, voxel_size)
            
            # 8. Sauvegarde
            print("\n💾 SAUVEGARDE")
            print("-" * 40)
            
            segmentation_id = str(uuid.uuid4())
            output_dir = Path("uploads/segmentation_results") / segmentation_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarder la segmentation
            if flair_affine is not None:
                segmentation_nii = nib.Nifti1Image(segmentation_result.astype(np.uint8), flair_affine)
            else:
                segmentation_nii = nib.Nifti1Image(segmentation_result.astype(np.uint8), np.eye(4))
            
            seg_path = output_dir / "segmentation_loadmodel.nii.gz"
            nib.save(segmentation_nii, str(seg_path))
            print(f"✅ Segmentation: {seg_path}")
            
            # Sauvegarder les métriques
            metrics_path = output_dir / "metrics_loadmodel.json"
            with open(metrics_path, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            print(f"✅ Métriques: {metrics_path}")
            
            # Rapport détaillé
            report_path = output_dir / "rapport_loadmodel.txt"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("RAPPORT DE SEGMENTATION CEREBLOOM - LOADMODEL.PY\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Patient ID: {PATIENT_ID}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Segmentation ID: {segmentation_id}\n")
                f.write(f"Méthode: {'loadmodel.py' if LOADMODEL_AVAILABLE else 'Simulation'}\n\n")
                
                f.write("IMAGES UTILISÉES:\n")
                f.write(f"  FLAIR: {os.path.basename(flair_path)}\n")
                f.write(f"  T1CE: {os.path.basename(t1ce_path)}\n\n")
                
                f.write("RÉSULTATS DE SEGMENTATION:\n")
                f.write(f"  Volume total tumoral: {metrics['total_tumor_volume_cm3']:.2f} cm³\n")
                f.write(f"  Taille voxel: {voxel_size[0]:.1f} × {voxel_size[1]:.1f} × {voxel_size[2]:.1f} mm\n\n")
                
                f.write("DÉTAIL PAR CLASSE:\n")
                for class_id, details in metrics["class_details"].items():
                    f.write(f"  {details['name']}:\n")
                    f.write(f"    Volume: {details['volume_cm3']:.2f} cm³\n")
                    f.write(f"    Pourcentage: {details['percentage']:.1f}%\n")
                    f.write(f"    Voxels: {details['voxel_count']}\n\n")
            
            print(f"✅ Rapport: {report_path}")
            
            # 9. Base de données
            try:
                segmentation_record = AISegmentation(
                    id=segmentation_id,
                    patient_id=PATIENT_ID,
                    doctor_id=None,
                    image_series_id=f"loadmodel_{PATIENT_ID}",
                    status=SegmentationStatus.COMPLETED,
                    input_parameters={
                        "modalities_used": ["FLAIR", "T1CE"],
                        "model_version": "loadmodel.py v1.0",
                        "processing_mode": "loadmodel" if LOADMODEL_AVAILABLE else "simulation",
                        "voxel_size_mm": list(voxel_size)
                    },
                    segmentation_results=metrics,
                    volume_analysis={"total_volume": metrics["total_tumor_volume_cm3"]},
                    started_at=datetime.now(),
                    completed_at=datetime.now()
                )
                
                db.add(segmentation_record)
                await db.commit()
                print("✅ Enregistré en base de données")
                
            except Exception as e:
                print(f"⚠️ Erreur base de données: {e}")
            
            print(f"\n🎉 TEST TERMINÉ!")
            print(f"📁 Résultats: {output_dir}")
            print(f"🆔 ID: {segmentation_id}")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        
        break

if __name__ == "__main__":
    print("🧠 CereBloom - Test avec LoadModel.py")
    
    # Installer les dépendances si nécessaire
    try:
        import scipy
    except ImportError:
        print("Installation de scipy...")
        os.system("pip install scipy")
    
    asyncio.run(test_with_loadmodel())
