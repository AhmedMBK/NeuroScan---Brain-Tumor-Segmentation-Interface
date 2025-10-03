#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API Flask pour la segmentation de tumeurs cérébrales.
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

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import werkzeug.utils

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

# Définition des couleurs pour la visualisation (couleurs plus vives)
colors = [
    (0, 0, 0),           # Noir pour le fond (pas de tumeur)
    (255, 50, 50),       # Rouge vif pour la nécrose/core
    (50, 255, 50),       # Vert vif pour l'œdème
    (50, 50, 255)        # Bleu vif pour l'enhancing
]
cmap = ListedColormap([(c[0]/255, c[1]/255, c[2]/255) for c in colors])

# Création des répertoires temporaires et de résultats
TEMP_DIR = os.path.join(os.getcwd(), "temp_uploads")
RESULTS_DIR = os.path.join(os.getcwd(), "api_results")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Initialisation de l'application Flask
app = Flask(__name__)
# Activer CORS pour toutes les routes
CORS(app)

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

    # Vérifier s'il y a une tumeur détectée
    if np.max(tumor_presence) > 0.1:  # Seuil pour considérer qu'il y a une tumeur
        # Trouver la tranche avec la plus grande présence tumorale
        optimal_slice = np.argmax(tumor_presence)
    else:
        # Si aucune tumeur n'est détectée, utiliser une tranche au milieu
        optimal_slice = len(predictions) // 2
        print("Aucune tumeur significative détectée. Utilisation d'une tranche médiane.")

    return optimal_slice

def generate_segmentation_image(model_predictions, slice_idx, original_data, case_id):
    """Génère une image de segmentation pour une tranche donnée."""
    # Extraire les données originales
    flair, t1, t1ce, t2, _, _, _, _ = original_data

    # Créer une figure avec une résolution très élevée pour une meilleure qualité
    plt.figure(figsize=(24, 18), dpi=400)

    # Définir la disposition des sous-figures (similaire à votre notebook)
    # Une rangée avec 6 images: original, ground truth, all classes, edema, core, enhancing
    f, axarr = plt.subplots(1, 6, figsize=(24, 6))

    # Redimensionner l'image FLAIR pour l'affichage
    orig_img = cv2.resize(flair[:,:,slice_idx+VOLUME_START_AT], (IMG_SIZE, IMG_SIZE))

    # Afficher l'image originale
    axarr[0].imshow(orig_img, cmap="gray")
    axarr[0].set_title('Original image flair', fontsize=18)
    axarr[0].axis('off')

    # Emplacement pour la vérité terrain (non disponible dans l'API)
    axarr[1].imshow(orig_img, cmap="gray")
    axarr[1].set_title('Ground truth (non disponible)', fontsize=18)
    axarr[1].axis('off')

    # Préparer les masques pour l'affichage
    # Créer une image RGB pour toutes les classes combinées
    all_classes = np.zeros((IMG_SIZE, IMG_SIZE, 3))

    # Appliquer les couleurs pour chaque classe
    if np.any(edema_mask):
        all_classes[edema_mask] = [0, 255, 0]  # Vert pour l'œdème
    if np.any(core_mask):
        all_classes[core_mask] = [255, 0, 0]   # Rouge pour le core
    if np.any(enhancing_mask):
        all_classes[enhancing_mask] = [0, 0, 255]  # Bleu pour l'enhancing

    # Normaliser pour l'affichage
    all_classes = all_classes / 255.0

    # Afficher toutes les classes
    for i in range(2, 6):
        axarr[i].imshow(orig_img, cmap="gray")

    # Superposer toutes les classes avec une opacité de 0.3
    axarr[2].imshow(all_classes, alpha=0.3)
    axarr[2].set_title('all classes predicted', fontsize=18)
    axarr[2].axis('off')

    # Afficher chaque classe séparément
    # Core (nécrotique)
    core_display = np.zeros((IMG_SIZE, IMG_SIZE, 3))
    if np.any(core_mask):
        core_display[core_mask] = [255, 0, 0]  # Rouge
    axarr[3].imshow(core_display / 255.0, alpha=0.3)
    axarr[3].set_title(f'{SEGMENT_CLASSES[1]} predicted', fontsize=18)
    axarr[3].axis('off')

    # Œdème
    edema_display = np.zeros((IMG_SIZE, IMG_SIZE, 3))
    if np.any(edema_mask):
        edema_display[edema_mask] = [0, 255, 0]  # Vert
    axarr[4].imshow(edema_display / 255.0, alpha=0.3)
    axarr[4].set_title(f'{SEGMENT_CLASSES[2]} predicted', fontsize=18)
    axarr[4].axis('off')

    # Enhancing
    enhancing_display = np.zeros((IMG_SIZE, IMG_SIZE, 3))
    if np.any(enhancing_mask):
        enhancing_display[enhancing_mask] = [0, 0, 255]  # Bleu
    axarr[5].imshow(enhancing_display / 255.0, alpha=0.3)
    axarr[5].set_title(f'{SEGMENT_CLASSES[3]} predicted', fontsize=18)
    axarr[5].axis('off')

    # Vérifier si une tumeur est présente dans cette tranche
    tumor_pixels = np.sum(core_mask) + np.sum(edema_mask) + np.sum(enhancing_mask)
    if tumor_pixels < 10:  # Très peu de pixels de tumeur
        # Ajouter un message d'avertissement
        for i in range(6):
            axarr[i].text(0.5, 0.5, "Aucune tumeur significative détectée\ndans cette tranche",
                     horizontalalignment='center',
                     verticalalignment='center',
                     transform=axarr[i].transAxes,
                     color='white',
                     fontsize=18,
                     fontweight='bold',
                     bbox=dict(facecolor='red', alpha=0.7, boxstyle='round,pad=0.5'))

    # Extraire les probabilités pour chaque classe directement (comme dans votre notebook)
    # Cela permet d'avoir les mêmes résultats que dans votre notebook
    core_prob = model_predictions[slice_idx,:,:,1]
    edema_prob = model_predictions[slice_idx,:,:,2]
    enhancing_prob = model_predictions[slice_idx,:,:,3]

    # Appliquer un seuil pour obtenir les masques binaires (ajustable selon les besoins)
    threshold = 0.5
    core_mask = core_prob > threshold
    edema_mask = edema_prob > threshold
    enhancing_mask = enhancing_prob > threshold

    # Ajouter une légende améliorée
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, color=(1, 0, 0), alpha=0.3, label=SEGMENT_CLASSES[1]),
        plt.Rectangle((0, 0), 1, 1, color=(0, 1, 0), alpha=0.3, label=SEGMENT_CLASSES[2]),
        plt.Rectangle((0, 0), 1, 1, color=(0, 0, 1), alpha=0.3, label=SEGMENT_CLASSES[3])
    ]

    # Créer une légende plus visible avec un fond blanc semi-transparent et une bordure
    for i in range(2, 6):
        legend = axarr[i].legend(handles=legend_elements, loc='upper right', fontsize=14,
                          framealpha=0.8, facecolor='white', edgecolor='black')

    plt.tight_layout()

    # Sauvegarder l'image
    output_path = os.path.join(RESULTS_DIR, f'{case_id}_segmentation.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

    return output_path

@app.route('/')
def home():
    """Page d'accueil de l'API."""
    return jsonify({
        "message": "API de Segmentation de Tumeurs Cérébrales",
        "status": "active",
        "endpoints": {
            "/": "Cette page d'accueil",
            "/status": "Vérifier le statut de l'API",
            "/segment": "Segmenter une tumeur cérébrale (POST)",
            "/results/<filename>": "Récupérer une image de résultat"
        }
    })

@app.route('/status')
def status():
    """Vérifie le statut de l'API et du modèle."""
    model_loaded = load_model_if_needed()
    return jsonify({
        "api_status": "active",
        "model_loaded": model_loaded,
        "tensorflow_version": tf.__version__
    })

@app.route('/segment', methods=['POST'])
def segment_tumor():
    """Segmente une tumeur cérébrale à partir des fichiers NIfTI téléchargés."""
    try:
        # Vérifier si les fichiers sont présents dans la requête
        if 'flair' not in request.files or 't1' not in request.files or 't1ce' not in request.files or 't2' not in request.files:
            return jsonify({"error": "Tous les fichiers (flair, t1, t1ce, t2) sont requis"}), 400

        # Récupérer les fichiers
        flair_file = request.files['flair']
        t1_file = request.files['t1']
        t1ce_file = request.files['t1ce']
        t2_file = request.files['t2']

        # Récupérer l'ID du cas s'il est fourni
        case_id = request.form.get('case_id', f"case_{uuid.uuid4().hex[:8]}")

        # Créer un répertoire temporaire pour ce cas
        case_dir = os.path.join(TEMP_DIR, case_id)
        os.makedirs(case_dir, exist_ok=True)

        # Sauvegarder les fichiers téléchargés
        flair_path = os.path.join(case_dir, f"{case_id}_flair.nii")
        t1_path = os.path.join(case_dir, f"{case_id}_t1.nii")
        t1ce_path = os.path.join(case_dir, f"{case_id}_t1ce.nii")
        t2_path = os.path.join(case_dir, f"{case_id}_t2.nii")

        flair_file.save(flair_path)
        t1_file.save(t1_path)
        t1ce_file.save(t1ce_path)
        t2_file.save(t2_path)

        # Charger le modèle si nécessaire
        if not load_model_if_needed():
            return jsonify({"error": "Erreur lors du chargement du modèle"}), 500

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

        # Nettoyer les fichiers temporaires
        if os.path.exists(case_dir):
            shutil.rmtree(case_dir)

        # Retourner le chemin de l'image et les statistiques
        return jsonify({
            "message": "Segmentation réussie",
            "case_id": case_id,
            "segmentation_image_url": f"/api_results/{case_id}_segmentation.png",
            "tumor_statistics": tumor_stats
        })

    except Exception as e:
        # Nettoyer les fichiers temporaires en cas d'erreur
        if 'case_dir' in locals() and os.path.exists(case_dir):
            shutil.rmtree(case_dir)
        return jsonify({"error": f"Erreur lors de la segmentation: {str(e)}"}), 500

@app.route('/results/<filename>')
def get_result(filename):
    """Récupère une image de résultat par son nom de fichier (pour compatibilité)."""
    file_path = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(file_path):
        # Essayer dans le dossier api_results
        api_file_path = os.path.join(RESULTS_DIR, filename)
        if os.path.exists(api_file_path):
            return send_file(api_file_path)
        return jsonify({"error": "Fichier non trouvé"}), 404
    return send_file(file_path)

@app.route('/api_results/<filename>')
def get_api_result(filename):
    """Récupère une image de résultat par son nom de fichier depuis le dossier api_results."""
    file_path = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "Fichier non trouvé"}), 404
    return send_file(file_path)

@app.route('/swagger')
def swagger_ui():
    """Sert l'interface Swagger UI."""
    swagger_html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interface Swagger pour l'API de Segmentation de Tumeurs Cérébrales</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css">
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
            }
            .header {
                background-color: #1b1b1b;
                color: white;
                padding: 20px;
                text-align: center;
            }
            .container {
                margin: 0 auto;
                max-width: 1200px;
                padding: 20px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>API de Segmentation de Tumeurs Cérébrales</h1>
            <p>Interface Swagger pour tester l'API</p>
        </div>
        <div class="container">
            <div id="swagger-ui"></div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    spec: {
                        openapi: "3.0.0",
                        info: {
                            title: "API de Segmentation de Tumeurs Cérébrales",
                            description: "Cette API permet de segmenter des tumeurs cérébrales à partir d'images IRM au format NIfTI.",
                            version: "1.0.0"
                        },
                        servers: [
                            {
                                url: window.location.origin,
                                description: "Serveur local"
                            }
                        ],
                        paths: {
                            "/": {
                                get: {
                                    summary: "Page d'accueil",
                                    description: "Retourne des informations sur l'API",
                                    responses: {
                                        "200": {
                                            description: "Informations sur l'API",
                                            content: {
                                                "application/json": {
                                                    schema: {
                                                        type: "object",
                                                        properties: {
                                                            message: { type: "string" },
                                                            status: { type: "string" },
                                                            endpoints: { type: "object" }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "/status": {
                                get: {
                                    summary: "Statut de l'API",
                                    description: "Vérifie le statut de l'API et du modèle",
                                    responses: {
                                        "200": {
                                            description: "Statut de l'API",
                                            content: {
                                                "application/json": {
                                                    schema: {
                                                        type: "object",
                                                        properties: {
                                                            api_status: { type: "string" },
                                                            model_loaded: { type: "boolean" },
                                                            tensorflow_version: { type: "string" }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "/segment": {
                                post: {
                                    summary: "Segmenter une tumeur cérébrale",
                                    description: "Segmente une tumeur cérébrale à partir des fichiers NIfTI téléchargés",
                                    requestBody: {
                                        content: {
                                            "multipart/form-data": {
                                                schema: {
                                                    type: "object",
                                                    properties: {
                                                        flair: {
                                                            type: "string",
                                                            format: "binary",
                                                            description: "Fichier NIfTI FLAIR"
                                                        },
                                                        t1: {
                                                            type: "string",
                                                            format: "binary",
                                                            description: "Fichier NIfTI T1"
                                                        },
                                                        t1ce: {
                                                            type: "string",
                                                            format: "binary",
                                                            description: "Fichier NIfTI T1ce"
                                                        },
                                                        t2: {
                                                            type: "string",
                                                            format: "binary",
                                                            description: "Fichier NIfTI T2"
                                                        },
                                                        case_id: {
                                                            type: "string",
                                                            description: "Identifiant du cas (optionnel)"
                                                        }
                                                    },
                                                    required: ["flair", "t1", "t1ce", "t2"]
                                                }
                                            }
                                        }
                                    },
                                    responses: {
                                        "200": {
                                            description: "Segmentation réussie",
                                            content: {
                                                "application/json": {
                                                    schema: {
                                                        type: "object",
                                                        properties: {
                                                            message: { type: "string" },
                                                            case_id: { type: "string" },
                                                            segmentation_image_url: { type: "string" },
                                                            tumor_statistics: { type: "object" }
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "400": {
                                            description: "Requête invalide",
                                            content: {
                                                "application/json": {
                                                    schema: {
                                                        type: "object",
                                                        properties: {
                                                            error: { type: "string" }
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "500": {
                                            description: "Erreur serveur",
                                            content: {
                                                "application/json": {
                                                    schema: {
                                                        type: "object",
                                                        properties: {
                                                            error: { type: "string" }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "/results/{filename}": {
                                get: {
                                    summary: "Récupérer une image de résultat",
                                    description: "Récupère une image de résultat par son nom de fichier",
                                    parameters: [
                                        {
                                            name: "filename",
                                            in: "path",
                                            required: true,
                                            schema: {
                                                type: "string"
                                            },
                                            description: "Nom du fichier image"
                                        }
                                    ],
                                    responses: {
                                        "200": {
                                            description: "Image de résultat",
                                            content: {
                                                "image/png": {
                                                    schema: {
                                                        type: "string",
                                                        format: "binary"
                                                    }
                                                }
                                            }
                                        },
                                        "404": {
                                            description: "Fichier non trouvé",
                                            content: {
                                                "application/json": {
                                                    schema: {
                                                        type: "object",
                                                        properties: {
                                                            error: { type: "string" }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout"
                });
            };
        </script>
    </body>
    </html>
    """
    return render_template_string(swagger_html)

if __name__ == "__main__":
    print("Démarrage de l'API Flask sur http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
