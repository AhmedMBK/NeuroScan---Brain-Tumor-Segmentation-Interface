#!/usr/bin/env python3
"""
🧠 Test Complet du Workflow CereBloom
Test automatisé : Upload Images → Segmentation → Visualisation
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
PATIENT_ID = "stringd5f01d3b-b54b-43a2-ba3c-0b12c797affc"

# Données de test pour l'authentification
TEST_USER = {
    "email": "admin@cerebloom.com",
    "password": "admin123"
}

def test_authentication():
    """Test de l'authentification"""
    print("🔐 Test d'authentification...")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=TEST_USER
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Authentification réussie")
        return token
    else:
        print(f"❌ Échec authentification: {response.status_code}")
        print(f"   Réponse: {response.text}")
        return None

def test_patient_exists(token):
    """Vérifier que le patient existe"""
    print(f"👤 Vérification du patient {PATIENT_ID}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/patients/{PATIENT_ID}",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ Patient trouvé")
        return True
    else:
        print(f"❌ Patient non trouvé: {response.status_code}")
        return False

def test_images_uploaded(token):
    """Vérifier que les images sont uploadées"""
    print("📁 Vérification des images uploadées...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/images/patient/{PATIENT_ID}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        images = data.get("images", [])
        print(f"✅ {len(images)} images trouvées")
        
        modalities = [img.get("modality") for img in images]
        print(f"   Modalités: {modalities}")
        return len(images) > 0
    else:
        print(f"❌ Erreur récupération images: {response.status_code}")
        return False

def test_launch_segmentation(token):
    """Lancer la segmentation avec votre modèle professionnel"""
    print("🧠 Lancement de la segmentation professionnelle...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/api/v1/segmentation/process-patient/{PATIENT_ID}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        segmentation_id = data.get("segmentation_id")
        print(f"✅ Segmentation lancée: {segmentation_id}")
        print(f"   Modalités utilisées: {data.get('available_modalities', [])}")
        print(f"   Modèle: {data.get('model_info', {}).get('model_type', 'N/A')}")
        return segmentation_id
    else:
        print(f"❌ Échec lancement segmentation: {response.status_code}")
        print(f"   Réponse: {response.text}")
        return None

def test_monitor_segmentation(token, segmentation_id):
    """Surveiller le statut de la segmentation"""
    print(f"⏱️ Surveillance de la segmentation {segmentation_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    max_attempts = 30  # 5 minutes max
    attempt = 0
    
    while attempt < max_attempts:
        response = requests.get(
            f"{BASE_URL}/api/v1/segmentation/status/{segmentation_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "UNKNOWN")
            
            print(f"   Tentative {attempt + 1}: Statut = {status}")
            
            if status == "COMPLETED":
                print("✅ Segmentation terminée avec succès!")
                return True
            elif status == "FAILED":
                print("❌ Segmentation échouée")
                return False
            elif status in ["PROCESSING", "PENDING"]:
                print(f"   ⏳ En cours... (attente 10s)")
                time.sleep(10)
            else:
                print(f"   ⚠️ Statut inattendu: {status}")
                time.sleep(5)
        else:
            print(f"   ❌ Erreur statut: {response.status_code}")
            time.sleep(5)
        
        attempt += 1
    
    print("⏰ Timeout - Segmentation trop longue")
    return False

def test_get_results(token, segmentation_id):
    """Récupérer les résultats de segmentation"""
    print(f"📊 Récupération des résultats {segmentation_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/segmentation/results/{segmentation_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Résultats récupérés:")
        
        # Afficher les métriques principales
        tumor_analysis = data.get("tumor_analysis", {})
        total_volume = tumor_analysis.get("total_volume_cm3", 0)
        print(f"   📈 Volume tumoral total: {total_volume} cm³")
        
        segments = tumor_analysis.get("tumor_segments", [])
        for segment in segments:
            name = segment.get("name", "N/A")
            volume = segment.get("volume_cm3", 0)
            percentage = segment.get("percentage", 0)
            print(f"   🎯 {name}: {volume} cm³ ({percentage}%)")
        
        return True
    else:
        print(f"❌ Erreur récupération résultats: {response.status_code}")
        return False

def test_get_visualization(token, segmentation_id):
    """Tester la visualisation"""
    print(f"🖼️ Test de visualisation {segmentation_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/segmentation/visualization/{segmentation_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ Visualisation générée")
        
        # Sauvegarder l'image
        output_path = f"test_visualization_{segmentation_id}.png"
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"   💾 Image sauvegardée: {output_path}")
        return True
    else:
        print(f"❌ Erreur visualisation: {response.status_code}")
        return False

def test_list_output_files(token, segmentation_id):
    """Lister les fichiers de sortie"""
    print(f"📂 Listage des fichiers de sortie {segmentation_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/segmentation/files/segmentation-outputs/{segmentation_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        files = data.get("files", [])
        print(f"✅ {len(files)} fichiers trouvés:")
        
        for file_info in files:
            filename = file_info.get("filename", "N/A")
            size_mb = file_info.get("size_mb", 0)
            file_type = file_info.get("file_type", "N/A")
            print(f"   📄 {filename} ({size_mb} MB) - {file_type}")
        
        folder_path = data.get("folder_path", "N/A")
        print(f"   📁 Dossier: {folder_path}")
        return True
    else:
        print(f"❌ Erreur listage fichiers: {response.status_code}")
        return False

def main():
    """Test complet du workflow"""
    print("🧠 CEREBLOOM - TEST COMPLET DU WORKFLOW")
    print("=" * 60)
    print(f"🎯 Patient ID: {PATIENT_ID}")
    print(f"🌐 Base URL: {BASE_URL}")
    print("=" * 60)
    
    # 1. Authentification
    token = test_authentication()
    if not token:
        print("❌ Échec du workflow - Authentification impossible")
        return
    
    print()
    
    # 2. Vérification du patient
    if not test_patient_exists(token):
        print("❌ Échec du workflow - Patient non trouvé")
        return
    
    print()
    
    # 3. Vérification des images
    if not test_images_uploaded(token):
        print("❌ Échec du workflow - Images non trouvées")
        return
    
    print()
    
    # 4. Lancement de la segmentation
    segmentation_id = test_launch_segmentation(token)
    if not segmentation_id:
        print("❌ Échec du workflow - Segmentation non lancée")
        return
    
    print()
    
    # 5. Surveillance de la segmentation
    if not test_monitor_segmentation(token, segmentation_id):
        print("❌ Échec du workflow - Segmentation non terminée")
        return
    
    print()
    
    # 6. Récupération des résultats
    if not test_get_results(token, segmentation_id):
        print("⚠️ Résultats non récupérés")
    
    print()
    
    # 7. Test de visualisation
    if not test_get_visualization(token, segmentation_id):
        print("⚠️ Visualisation non générée")
    
    print()
    
    # 8. Listage des fichiers
    if not test_list_output_files(token, segmentation_id):
        print("⚠️ Fichiers non listés")
    
    print()
    print("🎉 WORKFLOW COMPLET TESTÉ!")
    print(f"🆔 Segmentation ID: {segmentation_id}")
    print("=" * 60)

if __name__ == "__main__":
    main()
