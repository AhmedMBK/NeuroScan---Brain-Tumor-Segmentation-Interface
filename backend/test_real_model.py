#!/usr/bin/env python3
"""
🧠 Test du VRAI modèle my_model.h5
Vérification que l'API utilise bien votre modèle professionnel
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
PATIENT_ID = "stringd5f01d3b-b54b-43a2-ba3c-0b12c797affc"

def test_real_model():
    """Test avec votre vrai modèle"""
    print("🧠 TEST DU VRAI MODÈLE my_model.h5")
    print("=" * 60)
    
    # 1. Authentification
    print("🔐 Authentification...")
    try:
        auth_data = {
            "username": "admin@cerebloom.com",  # Utiliser username au lieu d'email
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=auth_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Authentification réussie")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Échec authentification : {response.status_code}")
            print(f"Réponse : {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Erreur authentification : {e}")
        return
    
    # 2. Lancer segmentation avec votre VRAI modèle
    print(f"\n🔥 Lancement segmentation avec VOTRE MODÈLE my_model.h5...")
    print(f"Patient ID : {PATIENT_ID}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/segmentation/process-patient/{PATIENT_ID}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            segmentation_id = data.get("segmentation_id")
            print(f"✅ Segmentation lancée : {segmentation_id}")
            
            # 3. Surveiller avec attention les logs
            print("\n⏱️ Surveillance de la segmentation (votre modèle doit se charger)...")
            
            for attempt in range(20):  # 20 tentatives = 2 minutes max
                time.sleep(6)  # Attendre 6 secondes
                
                try:
                    status_response = requests.get(
                        f"{BASE_URL}/api/v1/segmentation/status/{segmentation_id}",
                        headers=headers
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get("status", "UNKNOWN")
                        print(f"   Tentative {attempt + 1}/20 : {status}")
                        
                        if status == "COMPLETED":
                            print("🎉 SEGMENTATION TERMINÉE AVEC VOTRE MODÈLE !")
                            
                            # Récupérer les résultats détaillés
                            results_response = requests.get(
                                f"{BASE_URL}/api/v1/segmentation/results/{segmentation_id}",
                                headers=headers
                            )
                            
                            if results_response.status_code == 200:
                                results_data = results_response.json()
                                
                                print("\n📊 RÉSULTATS AVEC VOTRE MODÈLE :")
                                print("=" * 50)
                                
                                tumor_analysis = results_data.get("tumor_analysis", {})
                                total_volume = tumor_analysis.get("total_volume_cm3", 0)
                                print(f"📈 Volume tumoral total : {total_volume} cm³")
                                
                                # Vérifier si c'est réaliste (votre modèle donne ~35-45 cm³)
                                if 20 <= total_volume <= 100:
                                    print("✅ VOLUME RÉALISTE - Votre modèle fonctionne !")
                                elif total_volume > 500:
                                    print("❌ VOLUME TROP ÉLEVÉ - Simulation encore active")
                                else:
                                    print("⚠️ Volume inattendu")
                                
                                segments = tumor_analysis.get("tumor_segments", [])
                                for segment in segments:
                                    name = segment.get("name", "N/A")
                                    volume = segment.get("volume_cm3", 0)
                                    percentage = segment.get("percentage", 0)
                                    print(f"   🎯 {name}: {volume} cm³ ({percentage}%)")
                                
                                # Métriques de qualité
                                clinical_metrics = results_data.get("clinical_metrics", {})
                                dice = clinical_metrics.get("dice_coefficient", 0)
                                print(f"\n🎯 Dice Coefficient : {dice}")
                                
                                if dice > 0.8:
                                    print("✅ EXCELLENTE QUALITÉ - Votre modèle professionnel !")
                                
                                # Informations sur le modèle utilisé
                                model_info = results_data.get("model_info", {})
                                model_version = model_info.get("model_version", "N/A")
                                print(f"🧠 Modèle utilisé : {model_version}")
                                
                                return segmentation_id
                                
                            break
                            
                        elif status == "FAILED":
                            print("❌ Segmentation échouée")
                            break
                            
                    else:
                        print(f"   ⚠️ Erreur statut : {status_response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Erreur surveillance : {e}")
                    break
            
            print("⏰ Timeout - Vérifiez les logs du serveur")
            
        else:
            print(f"❌ Échec lancement : {response.status_code}")
            print(f"Réponse : {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur segmentation : {e}")

def check_output_files(segmentation_id):
    """Vérifier les fichiers de sortie"""
    if not segmentation_id:
        return
        
    print(f"\n📂 Vérification des fichiers de sortie...")
    
    import os
    from pathlib import Path
    
    output_dir = Path(f"uploads/segmentation_results/{segmentation_id}")
    
    if output_dir.exists():
        print(f"✅ Dossier trouvé : {output_dir}")
        
        files = list(output_dir.glob("*"))
        print(f"📄 {len(files)} fichiers générés :")
        
        for file_path in files:
            if file_path.is_file():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"   📄 {file_path.name} ({size_mb:.2f} MB)")
                
                # Vérifier le fichier de métriques
                if "metrics" in file_path.name and file_path.suffix == ".json":
                    try:
                        with open(file_path, 'r') as f:
                            metrics = json.load(f)
                            total_vol = metrics.get("total_tumor_volume_cm3", 0)
                            print(f"      📊 Volume dans métriques : {total_vol} cm³")
                    except:
                        pass
    else:
        print(f"❌ Dossier non trouvé : {output_dir}")

if __name__ == "__main__":
    segmentation_id = test_real_model()
    check_output_files(segmentation_id)
