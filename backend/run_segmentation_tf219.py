#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de test pour le modèle de segmentation de tumeur cérébrale.
Version compatible avec TensorFlow 2.19.0.
"""

import os
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

def load_and_preprocess_case(case_path):
    """
    Charge et prétraite les images MRI d'un cas.
    """
    # Trouver tous les fichiers .nii dans le dossier
    files = [f for f in os.listdir(case_path) if f.endswith('.nii')]

    # Extraire les chemins pour chaque modalité
    flair_path = [os.path.join(case_path, f) for f in files if 'flair' in f.lower()][0]
    t1_path = [os.path.join(case_path, f) for f in files if '_t1.' in f.lower()][0]
    t1ce_path = [os.path.join(case_path, f) for f in files if 't1ce' in f.lower()][0]
    t2_path = [os.path.join(case_path, f) for f in files if '_t2.' in f.lower()][0]

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

    # Utiliser flair et t1ce comme entrées du modèle (comme dans le notebook)
    for j in range(VOLUME_SLICES):
        X[j,:,:,0] = cv2.resize(flair_norm[:,:,j+VOLUME_START_AT], (IMG_SIZE, IMG_SIZE))
        X[j,:,:,1] = cv2.resize(t1ce_norm[:,:,j+VOLUME_START_AT], (IMG_SIZE, IMG_SIZE))

    # Retourner les données prétraitées et les données originales pour la visualisation
    return X, flair, t1, t1ce, t2, flair_norm, t1_norm, t1ce_norm, t2_norm

def predict_segmentation(model, preprocessed_data):
    """
    Prédit la segmentation à partir des données prétraitées.
    """
    return model.predict(preprocessed_data, verbose=1)

def find_optimal_slice(predictions):
    """
    Trouve la tranche optimale pour la visualisation.
    """
    # Calculer la somme des probabilités pour chaque classe tumorale par tranche
    tumor_presence = np.sum(predictions[:,:,:,1:], axis=(1,2,3))

    # Trouver la tranche avec la plus grande présence tumorale
    optimal_slice = np.argmax(tumor_presence)

    return optimal_slice

def visualize_results(model_predictions, slice_idx, original_data, case_name, output_dir):
    """
    Visualise les résultats de la segmentation.
    """
    # Extraire les données originales
    flair, t1, t1ce, t2, _, _, _, _ = original_data

    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)

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
    output_path = os.path.join(output_dir, f'{case_name}_segmentation.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

    print(f"Résultats sauvegardés dans {output_path}")

    return output_path

def main():
    """Fonction principale."""
    # Définir les chemins
    model_path = 'models/my_model.h5'
    test_cases_dir = 'images'
    output_dir = 'results'

    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)

    print("="*80)
    print("SEGMENTATION DE TUMEUR CÉRÉBRALE - OUTIL DE TEST (TF 2.19.0)")
    print("="*80)
    print(f"Modèle: {model_path}")
    print(f"Dossier de test: {test_cases_dir}")
    print(f"Dossier de sortie: {output_dir}")
    print("="*80)

    # Charger le modèle avec les métriques personnalisées
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
        # Essayer de charger le modèle avec TF 2.19.0
        print("Tentative de chargement du modèle...")
        
        # Option 1: Charger directement
        try:
            model = load_model(model_path, custom_objects=custom_objects, compile=False)
            print("Modèle chargé avec succès!")
        except Exception as e:
            print(f"Erreur lors du chargement direct: {str(e)}")
            
            # Option 2: Utiliser SavedModel
            print("Tentative de conversion du modèle H5 en SavedModel...")
            
            # Créer un répertoire temporaire pour le SavedModel
            temp_saved_model_dir = os.path.join(output_dir, 'temp_saved_model')
            os.makedirs(temp_saved_model_dir, exist_ok=True)
            
            # Utiliser h5py pour extraire l'architecture et les poids
            import h5py
            from tensorflow.keras.models import model_from_json
            
            try:
                with h5py.File(model_path, 'r') as f:
                    # Afficher les attributs disponibles
                    print("Attributs disponibles dans le fichier H5:")
                    for attr in f.attrs:
                        print(f"  - {attr}")
                    
                    # Essayer de récupérer la configuration du modèle
                    if 'model_config' in f.attrs:
                        model_config = f.attrs['model_config']
                        if isinstance(model_config, bytes):
                            model_config = model_config.decode('utf-8')
                        
                        # Créer le modèle à partir de l'architecture
                        model = model_from_json(model_config, custom_objects=custom_objects)
                        
                        # Charger les poids
                        model.load_weights(model_path)
                        print("Modèle chargé avec succès via h5py!")
                    else:
                        raise ValueError("Impossible de trouver la configuration du modèle dans le fichier H5.")
            except Exception as e2:
                print(f"Erreur lors de l'utilisation de h5py: {str(e2)}")
                raise ValueError("Impossible de charger le modèle. Essayez de le reconvertir avec TensorFlow 2.19.0.")
        
        # Compiler le modèle
        model.compile(
            loss="categorical_crossentropy",
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            metrics=['accuracy', tf.keras.metrics.MeanIoU(num_classes=4),
                     dice_coef, precision, sensitivity, specificity,
                     dice_coef_necrotic, dice_coef_edema, dice_coef_enhancing]
        )
        
        # Traiter chaque cas de test
        test_folders = [os.path.join(test_cases_dir, d) for d in os.listdir(test_cases_dir) if os.path.isdir(os.path.join(test_cases_dir, d))]
        
        for test_folder in test_folders:
            case_name = os.path.basename(test_folder)
            print(f"Traitement du cas: {case_name}")
            
            # Charger et prétraiter les données
            preprocessed_data, flair, t1, t1ce, t2, flair_norm, t1_norm, t1ce_norm, t2_norm = load_and_preprocess_case(test_folder)
            
            # Prédire la segmentation
            predictions = predict_segmentation(model, preprocessed_data)
            
            # Trouver la tranche optimale
            optimal_slice = find_optimal_slice(predictions)
            print(f"Tranche optimale: {optimal_slice}")
            
            # Visualiser les résultats
            original_data = (flair, t1, t1ce, t2, flair_norm, t1_norm, t1ce_norm, t2_norm)
            output_path = visualize_results(predictions, optimal_slice, original_data, case_name, output_dir)
            
            print(f"Segmentation terminée pour {case_name}. Résultats sauvegardés dans {output_path}")
            
    except Exception as e:
        print(f"Erreur lors de l'exécution: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
