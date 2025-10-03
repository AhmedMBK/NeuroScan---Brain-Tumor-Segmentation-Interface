#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API FastAPI pour la segmentation de tumeurs cérébrales.
Cette API permet de télécharger des fichiers NIfTI et d'obtenir des résultats de segmentation.
"""

import os
import io
import uuid
import shutil
import tempfile
import numpy as np
import tensorflow as tf
import nibabel as nib
import cv2
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
from sklearn.preprocessing import MinMaxScaler
import matplotlib
matplotlib.use('Agg')  # Pour générer des images sans affichage

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn

# Définition des constantes
IMG_SIZE = 128
VOLUME_SLICES = 100
VOLUME_START_AT = 22  # Première tranche du volume à inclure

# Définition des classes de segmentation
SEGMENT_CLASSES = {
    0: 'NOT tumor',
    1: 'NECROTIC/CORE',  # ou NON-ENHANCING tumor CORE
    2: 'EDEMA',
    3: 'ENHANCING'  # original 4 -> converti en 3
}

# Définition des couleurs pour la visualisation
colors = [
    (0, 0, 0),       # Noir pour le fond (pas de tumeur)
    (255, 0, 0),     # Rouge pour la nécrose/core
    (0, 255, 0),     # Vert pour l'œdème
    (0, 0, 255)      # Bleu pour l'enhancing
]
cmap = ListedColormap([(c[0]/255, c[1]/255, c[2]/255) for c in colors])

# Création des répertoires temporaires et de résultats
TEMP_DIR = os.path.join(os.getcwd(), "temp_uploads")
RESULTS_DIR = os.path.join(os.getcwd(), "api_results")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API de Segmentation de Tumeurs Cérébrales",
    description="Cette API permet de segmenter des tumeurs cérébrales à partir d'images IRM au format NIfTI.",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variable globale pour stocker le modèle chargé
model = None

# Définition des métriques personnalisées
def dice_coef(y_true, y_pred, smooth=1.0):
    """Coefficient Dice pour évaluer la similarité entre deux échantillons."""
    class_num = 4
    total_loss = 0
    for i in range(class_num):
        y_true_f = K.flatten(y_true[:,:,:,i])
        y_pred_f = K.flatten(y_pred[:,:,:,i])
        intersection = K.sum(y_true_f * y_pred_f)
        loss = ((2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth))
        total_loss += loss
    total_loss = total_loss / class_num
    return total_loss

def dice_coef_necrotic(y_true, y_pred, epsilon=1e-6):
    """Coefficient Dice pour la classe nécrotique."""
    intersection = K.sum(K.abs(y_true[:,:,:,1] * y_pred[:,:,:,1]))
    return (2. * intersection) / (K.sum(K.square(y_true[:,:,:,1])) + K.sum(K.square(y_pred[:,:,:,1])) + epsilon)

def dice_coef_edema(y_true, y_pred, epsilon=1e-6):
    """Coefficient Dice pour la classe œdème."""
    intersection = K.sum(K.abs(y_true[:,:,:,2] * y_pred[:,:,:,2]))
    return (2. * intersection) / (K.sum(K.square(y_true[:,:,:,2])) + K.sum(K.square(y_pred[:,:,:,2])) + epsilon)

def dice_coef_enhancing(y_true, y_pred, epsilon=1e-6):
    """Coefficient Dice pour la classe enhancing."""
    intersection = K.sum(K.abs(y_true[:,:,:,3] * y_pred[:,:,:,3]))
    return (2. * intersection) / (K.sum(K.square(y_true[:,:,:,3])) + K.sum(K.square(y_pred[:,:,:,3])) + epsilon)

def precision(y_true, y_pred):
    """Précision de la prédiction."""
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision

def sensitivity(y_true, y_pred):
    """Sensibilité (rappel) de la prédiction."""
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    return true_positives / (possible_positives + K.epsilon())

def specificity(y_true, y_pred):
    """Spécificité de la prédiction."""
    true_negatives = K.sum(K.round(K.clip((1-y_true) * (1-y_pred), 0, 1)))
    possible_negatives = K.sum(K.round(K.clip(1-y_true, 0, 1)))
    return true_negatives / (possible_negatives + K.epsilon())

def load_model_if_needed():
    """Charge le modèle s'il n'est pas déjà chargé."""
    global model
    if model is None:
        model_path = 'models/my_model.h5'
        
        # Définir les objets personnalisés
        custom_objects = {
            "dice_coef": dice_coef,
            "precision": precision,
            "sensitivity": sensitivity,
            "specificity": specificity,
            "dice_coef_necrotic": dice_coef_necrotic,
            "dice_coef_edema": dice_coef_edema,
            "dice_coef_enhancing": dice_coef_enhancing
        }
        
        try:
            # Charger le modèle
            model = load_model(model_path, custom_objects=custom_objects, compile=False)
            
            # Compiler le modèle
            model.compile(
                loss="categorical_crossentropy",
                optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                metrics=['accuracy', tf.keras.metrics.MeanIoU(num_classes=4),
                        dice_coef, precision, sensitivity, specificity,
                        dice_coef_necrotic, dice_coef_edema, dice_coef_enhancing]
            )
            return True
        except Exception as e:
            print(f"Erreur lors du chargement du modèle: {str(e)}")
            return False
    return True

def preprocess_nifti_files(flair_path, t1_path, t1ce_path, t2_path):
    """Prétraite les fichiers NIfTI pour la segmentation."""
    # Charger les données NIfTI
    flair = nib.load(flair_path).get_fdata()
    t1 = nib.load(t1_path).get_fdata()
    t1ce = nib.load(t1ce_path).get_fdata()
    t2 = nib.load(t2_path).get_fdata()

    # Normaliser les données
    scaler = MinMaxScaler()
    flair_norm = scaler.fit_transform(flair.reshape(-1, flair.shape[-1])).reshape(flair.shape)
    t1_norm = scaler.fit_transform(t1.reshape(-1, t1.shape[-1])).reshape(t1.shape)
    t1ce_norm = scaler.fit_transform(t1ce.reshape(-1, t1ce.shape[-1])).reshape(t1ce.shape)
    t2_norm = scaler.fit_transform(t2.reshape(-1, t2.shape[-1])).reshape(t2.shape)

    # Préparer les données pour le modèle
    X = np.empty((VOLUME_SLICES, IMG_SIZE, IMG_SIZE, 2))

    # Utiliser flair et t1ce comme entrées du modèle
    for j in range(VOLUME_SLICES):
        X[j,:,:,0] = cv2.resize(flair_norm[:,:,j+VOLUME_START_AT], (IMG_SIZE, IMG_SIZE))
        X[j,:,:,1] = cv2.resize(t1ce_norm[:,:,j+VOLUME_START_AT], (IMG_SIZE, IMG_SIZE))

    return X, flair, t1, t1ce, t2, flair_norm, t1_norm, t1ce_norm, t2_norm

def find_optimal_slice(predictions):
    """Trouve la tranche optimale pour la visualisation."""
    # Calculer la somme des probabilités pour chaque classe tumorale par tranche
    tumor_presence = np.sum(predictions[:,:,:,1:], axis=(1,2,3))

    # Trouver la tranche avec la plus grande présence tumorale
    optimal_slice = np.argmax(tumor_presence)

    return optimal_slice

def generate_segmentation_image(model_predictions, slice_idx, original_data, case_id):
    """Génère une image de segmentation pour une tranche donnée."""
    # Extraire les données originales
    flair, t1, t1ce, t2, _, _, _, _ = original_data

    # Créer une figure avec une résolution élevée
    plt.figure(figsize=(20, 16), dpi=300)

    # Définir la disposition des sous-figures
    gs = plt.GridSpec(2, 3, width_ratios=[1, 1, 1], height_ratios=[1, 1])

    # Afficher les modalités originales
    ax1 = plt.subplot(gs[0, 0])
    ax1.imshow(cv2.resize(t1[:,:,slice_idx+VOLUME_START_AT], (IMG_SIZE, IMG_SIZE)), cmap='gray')
    ax1.set_title('T1', fontsize=18)
    ax1.axis('off')

    ax2 = plt.subplot(gs[0, 1])
    ax2.imshow(cv2.resize(t1ce[:,:,slice_idx+VOLUME_START_AT], (IMG_SIZE, IMG_SIZE)), cmap='gray')
    ax2.set_title('T1ce', fontsize=18)
    ax2.axis('off')

    ax3 = plt.subplot(gs[0, 2])
    ax3.imshow(cv2.resize(t2[:,:,slice_idx+VOLUME_START_AT], (IMG_SIZE, IMG_SIZE)), cmap='gray')
    ax3.set_title('T2', fontsize=18)
    ax3.axis('off')

    ax4 = plt.subplot(gs[1, 0])
    ax4.imshow(cv2.resize(flair[:,:,slice_idx+VOLUME_START_AT], (IMG_SIZE, IMG_SIZE)), cmap='gray')
    ax4.set_title('FLAIR', fontsize=18)
    ax4.axis('off')

    # Afficher la segmentation prédite
    ax5 = plt.subplot(gs[1, 1:])

    # Fond de l'image en T1ce pour meilleure visualisation
    background = cv2.resize(t1ce[:,:,slice_idx+VOLUME_START_AT], (IMG_SIZE, IMG_SIZE))
    background = (background - background.min()) / (background.max() - background.min())

    # Créer une image RGB pour la segmentation
    segmentation = np.argmax(model_predictions[slice_idx], axis=-1)
    seg_rgb = np.zeros((IMG_SIZE, IMG_SIZE, 3))

    # Appliquer les couleurs à chaque classe
    for i in range(1, 4):  # Ignorer la classe 0 (fond)
        seg_rgb[segmentation == i] = colors[i]

    # Normaliser l'image RGB
    seg_rgb = seg_rgb / 255.0

    # Afficher l'image de fond
    ax5.imshow(background, cmap='gray')

    # Superposer la segmentation avec transparence
    mask = segmentation > 0
    ax5.imshow(np.ma.masked_array(seg_rgb, ~np.stack([mask, mask, mask], axis=-1)), alpha=0.7)

    # Ajouter une légende
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, color=tuple(c/255 for c in colors[1]), label=SEGMENT_CLASSES[1]),
        plt.Rectangle((0, 0), 1, 1, color=tuple(c/255 for c in colors[2]), label=SEGMENT_CLASSES[2]),
        plt.Rectangle((0, 0), 1, 1, color=tuple(c/255 for c in colors[3]), label=SEGMENT_CLASSES[3])
    ]
    ax5.legend(handles=legend_elements, loc='upper right', fontsize=14)

    ax5.set_title('Segmentation de la tumeur', fontsize=18)
    ax5.axis('off')

    plt.tight_layout()

    # Sauvegarder l'image
    output_path = os.path.join(RESULTS_DIR, f'{case_id}_segmentation.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

    return output_path

@app.get("/")
async def root():
    """Endpoint racine de l'API."""
    return {"message": "API de Segmentation de Tumeurs Cérébrales", "status": "active"}

@app.get("/status")
async def status():
    """Vérifie le statut de l'API et du modèle."""
    model_loaded = load_model_if_needed()
    return {
        "api_status": "active",
        "model_loaded": model_loaded,
        "tensorflow_version": tf.__version__
    }

@app.post("/segment")
async def segment_tumor(
    flair: UploadFile = File(..., description="Fichier NIfTI FLAIR"),
    t1: UploadFile = File(..., description="Fichier NIfTI T1"),
    t1ce: UploadFile = File(..., description="Fichier NIfTI T1ce"),
    t2: UploadFile = File(..., description="Fichier NIfTI T2"),
    case_id: Optional[str] = Form(None, description="Identifiant du cas (optionnel)")
):
    """
    Segmente une tumeur cérébrale à partir des fichiers NIfTI téléchargés.
    
    - **flair**: Fichier NIfTI FLAIR
    - **t1**: Fichier NIfTI T1
    - **t1ce**: Fichier NIfTI T1ce avec contraste
    - **t2**: Fichier NIfTI T2
    - **case_id**: Identifiant du cas (optionnel)
    
    Retourne l'image de segmentation et des statistiques sur la tumeur.
    """
    # Générer un ID de cas s'il n'est pas fourni
    if not case_id:
        case_id = f"case_{uuid.uuid4().hex[:8]}"
    
    # Créer un répertoire temporaire pour ce cas
    case_dir = os.path.join(TEMP_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    
    try:
        # Sauvegarder les fichiers téléchargés
        flair_path = os.path.join(case_dir, f"{case_id}_flair.nii")
        t1_path = os.path.join(case_dir, f"{case_id}_t1.nii")
        t1ce_path = os.path.join(case_dir, f"{case_id}_t1ce.nii")
        t2_path = os.path.join(case_dir, f"{case_id}_t2.nii")
        
        with open(flair_path, "wb") as f:
            f.write(await flair.read())
        with open(t1_path, "wb") as f:
            f.write(await t1.read())
        with open(t1ce_path, "wb") as f:
            f.write(await t1ce.read())
        with open(t2_path, "wb") as f:
            f.write(await t2.read())
        
        # Charger le modèle si nécessaire
        if not load_model_if_needed():
            raise HTTPException(status_code=500, detail="Erreur lors du chargement du modèle")
        
        # Prétraiter les données
        preprocessed_data, flair_data, t1_data, t1ce_data, t2_data, flair_norm, t1_norm, t1ce_norm, t2_norm = preprocess_nifti_files(
            flair_path, t1_path, t1ce_path, t2_path
        )
        
        # Prédire la segmentation
        predictions = model.predict(preprocessed_data, verbose=1)
        
        # Trouver la tranche optimale
        optimal_slice = find_optimal_slice(predictions)
        
        # Générer l'image de segmentation
        original_data = (flair_data, t1_data, t1ce_data, t2_data, flair_norm, t1_norm, t1ce_norm, t2_norm)
        output_path = generate_segmentation_image(predictions, optimal_slice, original_data, case_id)
        
        # Calculer les statistiques de la tumeur
        segmentation = np.argmax(predictions, axis=-1)
        tumor_stats = {
            "case_id": case_id,
            "optimal_slice": int(optimal_slice),
            "tumor_volume_pixels": int(np.sum(segmentation > 0)),
            "necrotic_core_pixels": int(np.sum(segmentation == 1)),
            "edema_pixels": int(np.sum(segmentation == 2)),
            "enhancing_pixels": int(np.sum(segmentation == 3)),
        }
        
        # Retourner le chemin de l'image et les statistiques
        return {
            "message": "Segmentation réussie",
            "case_id": case_id,
            "segmentation_image_url": f"/results/{case_id}_segmentation.png",
            "tumor_statistics": tumor_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la segmentation: {str(e)}")
    finally:
        # Nettoyer les fichiers temporaires
        if os.path.exists(case_dir):
            shutil.rmtree(case_dir)

@app.get("/results/{filename}")
async def get_result(filename: str):
    """Récupère une image de résultat par son nom de fichier."""
    file_path = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    return FileResponse(file_path)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
