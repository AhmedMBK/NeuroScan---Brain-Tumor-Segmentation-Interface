#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de test pour l'API de segmentation de tumeurs cérébrales.
Ce script envoie des fichiers NIfTI à l'API et affiche les résultats.
"""

import os
import requests
import json
import webbrowser
from pathlib import Path

# URL de l'API
API_URL = "http://localhost:8000"

def test_api_status():
    """Teste le statut de l'API."""
    try:
        response = requests.get(f"{API_URL}/status")
        if response.status_code == 200:
            print("API Status:")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"Erreur: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Erreur de connexion à l'API: {str(e)}")
        return False

def send_files_to_api(test_folder, case_id=None):
    """Envoie les fichiers NIfTI à l'API pour segmentation."""
    # Trouver tous les fichiers .nii dans le dossier
    files = [f for f in os.listdir(test_folder) if f.endswith('.nii')]
    
    # Extraire les chemins pour chaque modalité
    flair_path = [os.path.join(test_folder, f) for f in files if 'flair' in f.lower()][0]
    t1_path = [os.path.join(test_folder, f) for f in files if '_t1.' in f.lower()][0]
    t1ce_path = [os.path.join(test_folder, f) for f in files if 't1ce' in f.lower()][0]
    t2_path = [os.path.join(test_folder, f) for f in files if '_t2.' in f.lower()][0]
    
    # Préparer les fichiers pour l'envoi
    files_to_send = {
        'flair': open(flair_path, 'rb'),
        't1': open(t1_path, 'rb'),
        't1ce': open(t1ce_path, 'rb'),
        't2': open(t2_path, 'rb')
    }
    
    # Préparer les données du formulaire
    data = {}
    if case_id:
        data['case_id'] = case_id
    
    try:
        # Envoyer la requête à l'API
        print(f"Envoi des fichiers à l'API pour le cas: {case_id or Path(test_folder).name}")
        response = requests.post(f"{API_URL}/segment", files=files_to_send, data=data)
        
        # Fermer les fichiers
        for f in files_to_send.values():
            f.close()
        
        if response.status_code == 200:
            result = response.json()
            print("Résultat de la segmentation:")
            print(json.dumps(result, indent=2))
            
            # Ouvrir l'image de segmentation dans le navigateur
            if 'segmentation_image_url' in result:
                image_url = f"{API_URL}{result['segmentation_image_url']}"
                print(f"Ouverture de l'image de segmentation: {image_url}")
                webbrowser.open(image_url)
            
            return result
        else:
            print(f"Erreur: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Erreur lors de l'envoi des fichiers: {str(e)}")
        # Fermer les fichiers en cas d'erreur
        for f in files_to_send.values():
            f.close()
        return None

def main():
    """Fonction principale."""
    print("="*80)
    print("TEST DE L'API DE SEGMENTATION DE TUMEURS CÉRÉBRALES")
    print("="*80)
    
    # Vérifier le statut de l'API
    if not test_api_status():
        print("L'API n'est pas accessible. Assurez-vous qu'elle est en cours d'exécution.")
        return
    
    # Ouvrir l'interface Swagger dans le navigateur
    print("Ouverture de l'interface Swagger...")
    webbrowser.open(f"{API_URL}/docs")
    
    # Demander à l'utilisateur s'il souhaite tester l'API avec un cas spécifique
    test_api = input("Voulez-vous tester l'API avec un cas spécifique? (o/n): ")
    if test_api.lower() == 'o':
        # Lister les dossiers de test disponibles
        test_dir = "images"
        test_folders = [os.path.join(test_dir, d) for d in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, d))]
        
        print("\nDossiers de test disponibles:")
        for i, folder in enumerate(test_folders):
            print(f"{i+1}. {os.path.basename(folder)}")
        
        # Demander à l'utilisateur de choisir un dossier
        choice = input("\nChoisissez un dossier (numéro): ")
        try:
            folder_index = int(choice) - 1
            if 0 <= folder_index < len(test_folders):
                selected_folder = test_folders[folder_index]
                case_id = os.path.basename(selected_folder)
                
                # Envoyer les fichiers à l'API
                send_files_to_api(selected_folder, case_id)
            else:
                print("Choix invalide.")
        except ValueError:
            print("Veuillez entrer un numéro valide.")
    else:
        print("Vous pouvez tester l'API manuellement via l'interface Swagger.")

if __name__ == "__main__":
    main()
