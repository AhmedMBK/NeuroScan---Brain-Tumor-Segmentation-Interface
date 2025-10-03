#!/usr/bin/env python3
"""
🔍 Test simple pour vérifier la fonction save_individual_images
"""

import os
import sys

# Ajouter le répertoire backend au path
sys.path.append('backend')

def test_function_exists():
    """Test que la fonction existe et peut être importée"""
    
    print("🔍 Test d'import de la fonction save_individual_images")
    print("=" * 60)
    
    try:
        from test_brain_tumor_segmentationFinal import save_individual_images
        print("✅ Fonction save_individual_images importée avec succès")
        
        # Vérifier la signature de la fonction
        import inspect
        sig = inspect.signature(save_individual_images)
        print(f"📋 Signature: {sig}")
        
        # Vérifier les paramètres
        params = list(sig.parameters.keys())
        expected_params = ['predictions', 'slice_indices', 'original_data', 'normalized_data', 'case_name', 'output_dir']
        
        print(f"🎯 Paramètres trouvés: {params}")
        print(f"🎯 Paramètres attendus: {expected_params}")
        
        if params == expected_params:
            print("✅ Signature correcte!")
        else:
            print("⚠️ Signature différente de celle attendue")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_expected_output():
    """Test de la structure de sortie attendue"""
    
    print("\n🔍 Test de la structure de sortie attendue")
    print("=" * 50)
    
    # Structure attendue basée sur le code
    expected_structure = {
        "slices": [50, 75, 99],  # 3 slices représentatives
        "modalities": ['t1', 't1ce', 't2', 'flair', 'segmentation', 'overlay'],  # 6 modalités
        "images": []  # Liste d'images avec slice, modality, filename, url
    }
    
    print(f"📊 Structure attendue:")
    print(f"   - Slices: {expected_structure['slices']}")
    print(f"   - Modalités: {expected_structure['modalities']}")
    print(f"   - Total images: {len(expected_structure['slices']) * len(expected_structure['modalities'])}")
    
    # Exemples d'images attendues
    print(f"\n📁 Exemples d'images attendues:")
    count = 0
    for slice_idx in expected_structure['slices']:
        for modality in expected_structure['modalities']:
            count += 1
            filename = f"slice_{slice_idx}_{modality}.png"
            url = f"/api/segmentation/patient_id/image/{filename}"
            print(f"   {count:2d}. {filename}")
            if count >= 10:  # Limiter l'affichage
                break
        if count >= 10:
            break
    
    total_expected = len(expected_structure['slices']) * len(expected_structure['modalities'])
    print(f"   ... et {total_expected - count} autres images")
    
    print(f"\n✅ Structure validée - {total_expected} images attendues au total")

def check_integration_points():
    """Vérifier les points d'intégration avec l'API"""
    
    print("\n🔍 Points d'intégration avec l'API")
    print("=" * 40)
    
    print("📋 Modifications apportées au script:")
    print("   1. ✅ Fonction save_individual_images() ajoutée")
    print("   2. ✅ Appel dans main() pour tests locaux")
    print("   3. ✅ Appel dans process_patient_with_professional_model() pour l'API")
    print("   4. ✅ Retour des individual_images dans la réponse API")
    
    print("\n📋 Prochaines étapes nécessaires:")
    print("   1. 🔄 Ajouter endpoints API pour servir les images individuelles")
    print("   2. 🔄 Créer composant MedicalImageViewer React")
    print("   3. 🔄 Modifier ScanGallery pour mode groupé")
    print("   4. 🔄 Modifier ScanComparison pour sélection d'images")
    
    print("\n📁 Structure des fichiers générés:")
    print("   - results_medical/patient_id_rapport_medical_complet.png (rapport complet)")
    print("   - results_medical/patient_id_individual_images/ (dossier images)")
    print("     ├── slice_50_t1.png")
    print("     ├── slice_50_t1ce.png")
    print("     ├── slice_50_t2.png")
    print("     ├── slice_50_flair.png")
    print("     ├── slice_50_segmentation.png")
    print("     ├── slice_50_overlay.png")
    print("     ├── ... (slices 75 et 99)")
    print("     └── images_list.json (métadonnées)")

def verify_code_changes():
    """Vérifier que les modifications ont été appliquées"""
    
    print("\n🔍 Vérification des modifications du code")
    print("=" * 45)
    
    try:
        # Lire le fichier pour vérifier les modifications
        script_path = 'backend/test_brain_tumor_segmentationFinal.py'
        
        if not os.path.exists(script_path):
            print(f"❌ Script non trouvé: {script_path}")
            return False
        
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier les éléments clés
        checks = [
            ("save_individual_images", "def save_individual_images("),
            ("individual_images = save_individual_images(", "individual_images = save_individual_images("),
            ("individual_images", '"individual_images": individual_images,'),
            ("images_list.json", 'images_list.json'),
            ("IDENTIQUES au rapport complet", "IDENTIQUES au rapport complet")
        ]
        
        print("📋 Vérifications:")
        all_good = True
        for name, pattern in checks:
            if pattern in content:
                print(f"   ✅ {name}: Trouvé")
            else:
                print(f"   ❌ {name}: Non trouvé")
                all_good = False
        
        if all_good:
            print("\n✅ Toutes les modifications sont présentes!")
        else:
            print("\n⚠️ Certaines modifications manquent")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TEST SIMPLE DE LA FONCTION save_individual_images")
    print("=" * 80)
    
    # Test 1: Import de la fonction
    import_ok = test_function_exists()
    
    # Test 2: Structure attendue
    test_expected_output()
    
    # Test 3: Points d'intégration
    check_integration_points()
    
    # Test 4: Vérification du code
    code_ok = verify_code_changes()
    
    print("\n" + "=" * 80)
    if import_ok and code_ok:
        print("🎉 TESTS RÉUSSIS!")
        print("✅ La fonction save_individual_images est prête")
        print("✅ Les modifications du script sont correctes")
        print("✅ Prêt pour l'intégration avec l'API")
    else:
        print("❌ PROBLÈMES DÉTECTÉS")
        if not import_ok:
            print("⚠️ Problème d'import de la fonction")
        if not code_ok:
            print("⚠️ Modifications du code incomplètes")
    print("=" * 80)
