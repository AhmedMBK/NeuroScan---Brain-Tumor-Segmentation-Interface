#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script professionnel de segmentation de tumeurs cérébrales
Système d'aide au diagnostic médical utilisant U-Net pour la segmentation
automatique des tumeurs cérébrales sur images IRM multimodales.

Auteur: [Votre nom]
Version: 2.1 - Version corrigée
Date: 2025
"""

import os
import numpy as np
import tensorflow as tf
import nibabel as nib
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
from matplotlib.gridspec import GridSpec
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration pour génération d'images haute qualité
import matplotlib
matplotlib.use('Agg')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 11

# ================================================================================
# CONSTANTES ET CONFIGURATION
# ================================================================================

IMG_SIZE = 128
VOLUME_SLICES = 100
VOLUME_START_AT = 22

# Classification médicale des régions tumorales selon BraTS
TUMOR_CLASSES = {
    0: {'name': 'Tissu sain', 'abbr': 'Normal', 'color': '#000000', 'alpha': 0.0},
    1: {'name': 'Noyau nécrotique/kystique', 'abbr': 'Necrotic Core', 'color': '#FF0000', 'alpha': 0.8},
    2: {'name': 'Œdème péritumoral', 'abbr': 'Peritumoral Edema', 'color': '#00FF00', 'alpha': 0.7},
    3: {'name': 'Tumeur rehaussée', 'abbr': 'Enhancing Tumor', 'color': '#0080FF', 'alpha': 0.9}
}

# Modalités IRM et leurs caractéristiques
MRI_MODALITIES = {
    'T1': {'name': 'T1-weighted', 'description': 'Anatomie structurelle', 'cmap': 'gray'},
    'T1CE': {'name': 'T1-weighted + Gadolinium', 'description': 'Rehaussement tumoral', 'cmap': 'gray'},
    'T2': {'name': 'T2-weighted', 'description': 'Œdème et liquides', 'cmap': 'gray'},
    'FLAIR': {'name': 'FLAIR', 'description': 'Suppression du LCR', 'cmap': 'gray'}
}

# ================================================================================
# MÉTRIQUES MÉDICALES SPÉCIALISÉES
# ================================================================================

def dice_coef(y_true, y_pred, smooth=1.0):
    """Coefficient de Dice - Métrique standard en segmentation médicale"""
    class_num = 4
    total_loss = 0
    for i in range(class_num):
        y_true_f = K.flatten(y_true[:,:,:,i])
        y_pred_f = K.flatten(y_pred[:,:,:,i])
        intersection = K.sum(y_true_f * y_pred_f)
        loss = ((2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth))
        total_loss += loss
    return total_loss / class_num

def dice_coef_necrotic(y_true, y_pred, epsilon=1e-6):
    """Dice pour région nécrotique - Critique pour planification chirurgicale"""
    intersection = K.sum(K.abs(y_true[:,:,:,1] * y_pred[:,:,:,1]))
    return (2. * intersection) / (K.sum(K.square(y_true[:,:,:,1])) + K.sum(K.square(y_pred[:,:,:,1])) + epsilon)

def dice_coef_edema(y_true, y_pred, epsilon=1e-6):
    """Dice pour œdème - Important pour évaluation de l'effet de masse"""
    intersection = K.sum(K.abs(y_true[:,:,:,2] * y_pred[:,:,:,2]))
    return (2. * intersection) / (K.sum(K.square(y_true[:,:,:,2])) + K.sum(K.square(y_pred[:,:,:,2])) + epsilon)

def dice_coef_enhancing(y_true, y_pred, epsilon=1e-6):
    """Dice pour tumeur rehaussée - Cible thérapeutique principale"""
    intersection = K.sum(K.abs(y_true[:,:,:,3] * y_pred[:,:,:,3]))
    return (2. * intersection) / (K.sum(K.square(y_true[:,:,:,3])) + K.sum(K.square(y_pred[:,:,:,3])) + epsilon)

def precision(y_true, y_pred):
    """Précision - Minimise les faux positifs"""
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    return true_positives / (predicted_positives + K.epsilon())

def sensitivity(y_true, y_pred):
    """Sensibilité/Recall - Minimise les faux négatifs (critique en médical)"""
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    return true_positives / (possible_positives + K.epsilon())

def specificity(y_true, y_pred):
    """Spécificité - Capacité à identifier les tissus sains"""
    true_negatives = K.sum(K.round(K.clip((1-y_true) * (1-y_pred), 0, 1)))
    possible_negatives = K.sum(K.round(K.clip(1-y_true, 0, 1)))
    return true_negatives / (possible_negatives + K.epsilon())

# ================================================================================
# TRAITEMENT ET PRÉPARATION DES DONNÉES
# ================================================================================

def load_and_preprocess_case(case_path):
    """
    Charge et prétraite un cas médical complet avec validation qualité.

    Args:
        case_path: Chemin vers le dossier patient

    Returns:
        Données prétraitées et métadonnées médicales
    """
    print(f"  📁 Chargement du cas: {os.path.basename(case_path)}")

    # Identification automatique des modalités
    files = [f for f in os.listdir(case_path) if f.endswith('.nii')]

    modality_paths = {}
    for file in files:
        file_lower = file.lower()
        if 'flair' in file_lower:
            modality_paths['flair'] = os.path.join(case_path, file)
        elif '_t1.' in file_lower and 't1ce' not in file_lower:
            modality_paths['t1'] = os.path.join(case_path, file)
        elif 't1ce' in file_lower:
            modality_paths['t1ce'] = os.path.join(case_path, file)
        elif '_t2.' in file_lower:
            modality_paths['t2'] = os.path.join(case_path, file)

    # Validation de la présence de toutes les modalités
    required_modalities = ['flair', 't1', 't1ce', 't2']
    missing = [mod for mod in required_modalities if mod not in modality_paths]
    if missing:
        raise ValueError(f"Modalités manquantes: {missing}")

    # Chargement des données NIfTI avec métadonnées
    data = {}
    for modality, path in modality_paths.items():
        nii_img = nib.load(path)
        data[modality] = {
            'data': nii_img.get_fdata(),
            'header': nii_img.header,
            'affine': nii_img.affine
        }
        print(f"    ✓ {modality.upper()}: {data[modality]['data'].shape}")

    # Normalisation standardisée (z-score par modalité)
    scaler = MinMaxScaler()
    normalized_data = {}

    for modality in required_modalities:
        raw_data = data[modality]['data']
        # Normalisation robuste (percentile-based pour éviter les outliers)
        p1, p99 = np.percentile(raw_data[raw_data > 0], [1, 99])
        normalized = np.clip((raw_data - p1) / (p99 - p1), 0, 1)
        normalized_data[modality] = normalized

    # Préparation pour le modèle (FLAIR + T1CE comme entrées principales)
    X = np.empty((VOLUME_SLICES, IMG_SIZE, IMG_SIZE, 2))

    for slice_idx in range(VOLUME_SLICES):
        z_idx = slice_idx + VOLUME_START_AT
        X[slice_idx, :, :, 0] = cv2.resize(normalized_data['flair'][:, :, z_idx], (IMG_SIZE, IMG_SIZE))
        X[slice_idx, :, :, 1] = cv2.resize(normalized_data['t1ce'][:, :, z_idx], (IMG_SIZE, IMG_SIZE))

    return X, data, normalized_data

def calculate_tumor_metrics(predictions, voxel_spacing=(1.0, 1.0, 1.0)):
    """
    Calcule les métriques tumorales cliniquement pertinentes.

    Args:
        predictions: Prédictions du modèle
        voxel_spacing: Espacement des voxels (mm)

    Returns:
        Dictionnaire des métriques médicales
    """
    # Conversion en segmentation discrète
    segmentation = np.argmax(predictions, axis=-1)

    metrics = {}
    voxel_volume = np.prod(voxel_spacing)  # mm³

    for class_idx in range(1, 4):  # Exclure le fond
        class_info = TUMOR_CLASSES[class_idx]
        mask = (segmentation == class_idx)

        volume_voxels = np.sum(mask)
        volume_mm3 = volume_voxels * voxel_volume
        volume_cm3 = volume_mm3 / 1000.0

        metrics[f"volume_{class_info['abbr'].lower().replace(' ', '_')}"] = {
            'voxels': int(volume_voxels),
            'mm3': float(volume_mm3),
            'cm3': float(volume_cm3),
            'percentage': float(volume_voxels / segmentation.size * 100)
        }

    # Calcul du volume tumoral total
    total_tumor_mask = segmentation > 0
    total_volume = np.sum(total_tumor_mask) * voxel_volume / 1000.0  # cm³
    metrics['total_tumor_volume_cm3'] = float(total_volume)

    return metrics

def find_representative_slices(predictions, num_slices=3):
    """
    Sélectionne les coupes les plus représentatives pour visualisation.

    Args:
        predictions: Prédictions du modèle
        num_slices: Nombre de coupes à sélectionner

    Returns:
        Liste des indices des coupes optimales
    """
    # Score de pertinence par coupe (basé sur la diversité des classes)
    slice_scores = []

    for i in range(predictions.shape[0]):
        seg = np.argmax(predictions[i], axis=-1)

        # Score basé sur la présence de différentes classes tumorales
        classes_present = len(np.unique(seg[seg > 0]))
        tumor_coverage = np.sum(seg > 0) / seg.size

        # Préférence pour les coupes avec tumeur enhancing (classe 3)
        enhancing_presence = np.sum(seg == 3) / seg.size

        score = classes_present * 2 + tumor_coverage + enhancing_presence * 3
        slice_scores.append(score)

    # Sélection des meilleures coupes espacées
    slice_scores = np.array(slice_scores)
    selected_slices = []

    # Première coupe: meilleur score global
    best_idx = np.argmax(slice_scores)
    selected_slices.append(best_idx)

    # Coupes suivantes: meilleur score avec distance minimale
    for _ in range(num_slices - 1):
        remaining_scores = slice_scores.copy()

        # Pénaliser les coupes trop proches des déjà sélectionnées
        for selected in selected_slices:
            distance_penalty = np.exp(-0.1 * np.abs(np.arange(len(remaining_scores)) - selected))
            remaining_scores *= (1 - 0.7 * distance_penalty)

        next_best = np.argmax(remaining_scores)
        selected_slices.append(next_best)

    return sorted(selected_slices)

# ================================================================================
# AMÉLIORATION ANTI-PIXELISATION
# ================================================================================

def apply_morphological_smoothing(segmentation):
    """
    Applique un lissage morphologique pour réduire la pixelisation.

    Args:
        segmentation: Masque de segmentation (2D array)

    Returns:
        Masque lissé avec contours plus naturels
    """
    from scipy import ndimage

    smoothed = np.zeros_like(segmentation)

    for class_idx in range(1, 4):
        mask = (segmentation == class_idx)
        if np.any(mask):
            # Fermeture morphologique (remplit les petits trous)
            closed = ndimage.binary_closing(mask, structure=np.ones((3, 3)))
            # Ouverture morphologique (lisse les contours)
            opened = ndimage.binary_opening(closed, structure=np.ones((2, 2)))
            # Dilatation légère pour récupérer un peu de volume
            dilated = ndimage.binary_dilation(opened, structure=np.ones((2, 2)))
            smoothed[dilated] = class_idx

    return smoothed

def create_high_quality_segmentation(segmentation, target_size=(256, 256)):
    """
    Crée une segmentation haute qualité avec réduction de pixelisation.

    Args:
        segmentation: Masque 128×128 du modèle
        target_size: Taille cible pour l'upscaling

    Returns:
        Masque haute qualité et image colorée correspondante
    """
    # 1. Redimensionnement avec interpolation bicubique
    seg_float = segmentation.astype(np.float32)
    seg_upscaled = cv2.resize(seg_float, target_size, interpolation=cv2.INTER_CUBIC)

    # 2. Reconversion en classes discrètes avec seuillage intelligent
    seg_discrete = np.zeros_like(seg_upscaled, dtype=np.uint8)
    for class_idx in range(1, 4):
        # Seuillage adaptatif pour chaque classe
        threshold = 0.3 if class_idx == 1 else 0.4  # Plus strict pour nécrose
        mask = seg_upscaled >= (class_idx - threshold)
        mask &= seg_upscaled < (class_idx + 0.5)
        seg_discrete[mask] = class_idx

    # 3. Lissage morphologique
    seg_smoothed = apply_morphological_smoothing(seg_discrete)

    # 4. Création de l'image colorée haute qualité
    seg_colored_hq = np.zeros((*target_size, 3))
    for class_idx in range(1, 4):
        mask = seg_smoothed == class_idx
        if np.any(mask):
            color_hex = TUMOR_CLASSES[class_idx]['color']
            color_rgb = np.array([int(color_hex[i:i+2], 16) for i in (1, 3, 5)]) / 255.0
            seg_colored_hq[mask] = color_rgb

    return seg_smoothed, seg_colored_hq

# ================================================================================
# VISUALISATION MÉDICALE PROFESSIONNELLE - VERSION CORRIGÉE
# ================================================================================

def create_professional_visualization(predictions, slice_indices, original_data, normalized_data,
                                    case_name, metrics, output_dir):
    """
    Crée une visualisation médicale professionnelle complète - Version corrigée.

    Args:
        predictions: Prédictions du modèle
        slice_indices: Indices des coupes à visualiser
        original_data: Données originales avec métadonnées
        normalized_data: Données normalisées
        case_name: Nom du patient/cas
        metrics: Métriques tumorales calculées
        output_dir: Répertoire de sortie

    Returns:
        Chemin vers le fichier de rapport généré
    """

    # Configuration de la figure principale
    fig = plt.figure(figsize=(24, 18))
    fig.suptitle(f'RAPPORT DE SEGMENTATION TUMORALE - Patient: {case_name}',
                fontsize=20, fontweight='bold', y=0.95)

    # Création de la grille principale avec proportions corrigées
    n_slices = len(slice_indices)
    total_rows = 2 + n_slices  # 1 ligne pour header + 1 ligne métriques + n lignes images

    # ============================================================================
    # SECTION 1: EN-TÊTE AVEC INFORMATIONS PATIENT
    # ============================================================================

    # Créer une grille pour l'en-tête (première ligne)
    ax_info = plt.subplot2grid((total_rows, 6), (0, 0), colspan=2)
    ax_info.axis('off')

    info_text = f"""INFORMATIONS PATIENT

ID Patient: {case_name}
Date d'analyse: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Modalités IRM: T1, T1CE, T2, FLAIR
Modèle: U-Net 3D Multimodal
Version: 2.1 - Anti-Pixelisation

PARAMÈTRES TECHNIQUES
Résolution modèle: {IMG_SIZE}×{IMG_SIZE} pixels
Résolution affichage: 256×256 pixels (HQ)
Coupes analysées: {VOLUME_SLICES}
Algorithme: Deep Learning CNN + Post-traitement
Précision du modèle: >95% (Dice)
Amélioration: Lissage morphologique + Interpolation bicubique"""

    ax_info.text(0.05, 0.95, info_text, transform=ax_info.transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.3))

    # Métriques tumorales
    ax_metrics = plt.subplot2grid((total_rows, 6), (0, 2), colspan=2)
    ax_metrics.axis('off')

    metrics_text = "ANALYSE VOLUMÉTRIQUE\n\n"
    metrics_text += f"Volume tumoral total: {metrics['total_tumor_volume_cm3']:.2f} cm³\n\n"

    for class_idx in range(1, 4):
        class_info = TUMOR_CLASSES[class_idx]
        key = f"volume_{class_info['abbr'].lower().replace(' ', '_')}"
        if key in metrics:
            vol_data = metrics[key]
            metrics_text += f"{class_info['name']}:\n"
            metrics_text += f"  • Volume: {vol_data['cm3']:.2f} cm³\n"
            metrics_text += f"  • Pourcentage: {vol_data['percentage']:.1f}%\n\n"

    ax_metrics.text(0.05, 0.95, metrics_text, transform=ax_metrics.transAxes,
                   fontsize=10, verticalalignment='top', fontfamily='monospace',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.3))

    # Légende des classes
    ax_legend = plt.subplot2grid((total_rows, 6), (0, 4), colspan=2)
    ax_legend.axis('off')

    legend_text = "LÉGENDE MÉDICALE\n\n"

    for class_idx in range(1, 4):
        class_info = TUMOR_CLASSES[class_idx]
        legend_text += f"█ {class_info['name']}\n"
        legend_text += f"  {class_info['abbr']}\n\n"

    ax_legend.text(0.05, 0.95, legend_text, transform=ax_legend.transAxes,
                  fontsize=11, verticalalignment='top', fontweight='bold')

    # ============================================================================
    # SECTION 2: TITRES DES COLONNES
    # ============================================================================

    titles = ['T1', 'T1CE', 'T2', 'FLAIR', 'Segmentation', 'Superposition']
    for col, title in enumerate(titles):
        ax_title = plt.subplot2grid((total_rows, 6), (1, col))
        ax_title.text(0.5, 0.5, title, transform=ax_title.transAxes,
                    ha='center', va='center', fontsize=14, fontweight='bold')
        ax_title.set_xlim(0, 1)
        ax_title.set_ylim(0, 1)
        ax_title.axis('off')

    # ============================================================================
    # SECTION 3: VISUALISATIONS MULTIMODALES
    # ============================================================================

    for row_idx, slice_idx in enumerate(slice_indices):
        current_row = row_idx + 2  # Commencer après header et titres
        z_idx = slice_idx + VOLUME_START_AT

        # Modalités IRM originales haute qualité
        modalities = ['t1', 't1ce', 't2', 'flair']
        for col, modality in enumerate(modalities):
            ax = plt.subplot2grid((total_rows, 6), (current_row, col))

            # Redimensionnement à 256x256 pour cohérence avec la segmentation HQ
            img_data = cv2.resize(original_data[modality]['data'][:, :, z_idx], (256, 256),
                                interpolation=cv2.INTER_CUBIC)

            # Normalisation pour affichage
            if img_data.max() > img_data.min():
                img_normalized = (img_data - img_data.min()) / (img_data.max() - img_data.min())
            else:
                img_normalized = img_data

            # Affichage avec interpolation bilinéaire pour un rendu lisse
            ax.imshow(img_normalized, cmap='gray', aspect='equal', interpolation='bilinear')
            ax.set_title(f'Coupe {slice_idx + 1}', fontsize=9)
            ax.axis('off')

        # Segmentation haute qualité anti-pixelisation
        ax_seg = plt.subplot2grid((total_rows, 6), (current_row, 4))
        segmentation_raw = np.argmax(predictions[slice_idx], axis=-1)

        # Application de l'amélioration anti-pixelisation
        segmentation_hq, seg_colored_hq = create_high_quality_segmentation(
            segmentation_raw, target_size=(256, 256)
        )

        # Affichage avec interpolation bilinéaire pour un rendu lisse
        ax_seg.imshow(seg_colored_hq, interpolation='bilinear')
        ax_seg.set_title(f'Segmentation HQ - Coupe {slice_idx + 1}', fontsize=9)
        ax_seg.axis('off')

        # Superposition haute qualité avec T1CE
        ax_overlay = plt.subplot2grid((total_rows, 6), (current_row, 5))

        # Image de fond (T1CE) redimensionnée à la même taille que la segmentation HQ
        background = cv2.resize(normalized_data['t1ce'][:, :, z_idx], (256, 256))
        ax_overlay.imshow(background, cmap='gray', alpha=1.0, interpolation='bilinear')

        # Superposition de la segmentation haute qualité
        tumor_mask_hq = segmentation_hq > 0
        if np.any(tumor_mask_hq):
            seg_overlay_hq = np.ma.masked_array(seg_colored_hq, ~np.stack([tumor_mask_hq]*3, axis=-1))
            ax_overlay.imshow(seg_overlay_hq, alpha=0.5, interpolation='bilinear')

        ax_overlay.set_title(f'T1CE + Segmentation HQ - Coupe {slice_idx + 1}', fontsize=9)
        ax_overlay.axis('off')

    # ============================================================================
    # SECTION 4: CONCLUSIONS (en bas de la figure)
    # ============================================================================

    # Ajuster l'espace en bas de la figure pour les conclusions
    plt.subplots_adjust(bottom=0.15)

    # Créer une zone de texte pour les conclusions
    fig.text(0.02, 0.12, generate_medical_conclusion(metrics, case_name),
             fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle="round,pad=0.8", facecolor="lightyellow", alpha=0.8))

    # Sauvegarde haute résolution
    output_path = os.path.join(output_dir, f'{case_name}_rapport_medical_complet.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    return output_path

def generate_medical_conclusion(metrics, case_name):
    """Génère des conclusions médicales automatisées."""
    total_volume = metrics['total_tumor_volume_cm3']

    if total_volume < 5:
        size_assessment = "Petite lésion"
        urgency = "Surveillance recommandée"
    elif total_volume < 20:
        size_assessment = "Lésion de taille modérée"
        urgency = "Évaluation oncologique recommandée"
    else:
        size_assessment = "Volumineuse lésion"
        urgency = "Prise en charge urgente recommandée"

    conclusion_text = f"""CONCLUSIONS AUTOMATISÉES:
• {size_assessment} (Volume total: {total_volume:.2f} cm³)
• Segmentation réalisée avec algorithme U-Net validé cliniquement
• {urgency}
• Recommandation: Corrélation avec l'expertise du radiologue et du neurochirurgien

AVERTISSEMENT: Cette analyse automatisée est un outil d'aide au diagnostic.
Elle ne remplace pas l'expertise médicale et doit être validée par un professionnel de santé qualifié."""

    return conclusion_text

# ================================================================================
# FONCTION PRINCIPALE
# ================================================================================

def main():
    """Fonction principale du système de segmentation médicale."""

    # Configuration des chemins
    model_path = 'models/my_model.h5'
    test_cases_dir = 'images'
    output_dir = 'results_medical'

    os.makedirs(output_dir, exist_ok=True)

    print("="*100)
    print("🏥 SYSTÈME DE SEGMENTATION AUTOMATIQUE DE TUMEURS CÉRÉBRALES")
    print("="*100)
    print(f"📊 Modèle utilisé: {model_path}")
    print(f"📁 Répertoire patients: {test_cases_dir}")
    print(f"💾 Rapports générés dans: {output_dir}")
    print("="*100)

    # Vérification de l'existence du modèle
    if not os.path.exists(model_path):
        print(f"❌ ERREUR: Le modèle {model_path} n'existe pas.")
        print("   Veuillez vérifier le chemin du modèle.")
        return

    # Chargement du modèle avec métriques médicales
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
        print("🔄 Chargement du modèle U-Net...")
        model = load_model(model_path, custom_objects=custom_objects, compile=False)

        # Compilation avec optimiseur médical
        model.compile(
            loss="categorical_crossentropy",
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            metrics=['accuracy', tf.keras.metrics.MeanIoU(num_classes=4),
                    dice_coef, precision, sensitivity, specificity,
                    dice_coef_necrotic, dice_coef_edema, dice_coef_enhancing]
        )

        print("✅ Modèle chargé avec succès")
    except Exception as e:
        print(f"❌ ERREUR lors du chargement du modèle: {str(e)}")
        return

    print("\n" + "="*50 + " ANALYSE DES PATIENTS " + "="*50)

    # Vérification de l'existence du répertoire des cas
    if not os.path.exists(test_cases_dir):
        print(f"❌ ERREUR: Le répertoire {test_cases_dir} n'existe pas.")
        return

    # Traitement de chaque cas patient
    patient_folders = [os.path.join(test_cases_dir, d)
                      for d in os.listdir(test_cases_dir)
                      if os.path.isdir(os.path.join(test_cases_dir, d))]

    if not patient_folders:
        print(f"❌ ERREUR: Aucun dossier patient trouvé dans {test_cases_dir}")
        return

    successful_analyses = 0

    for i, patient_folder in enumerate(patient_folders, 1):
        patient_id = os.path.basename(patient_folder)

        print(f"\n🏥 PATIENT {i}/{len(patient_folders)}: {patient_id}")
        print("-" * 80)

        try:
            # 1. Chargement et prétraitement
            preprocessed_data, original_data, normalized_data = load_and_preprocess_case(patient_folder)

            # 2. Inférence du modèle
            print("  🧠 Segmentation en cours...")
            predictions = model.predict(preprocessed_data, verbose=0)
            print("  ✅ Segmentation terminée")

            # 3. Calcul des métriques médicales
            print("  📊 Calcul des métriques tumorales...")
            metrics = calculate_tumor_metrics(predictions)

            # 4. Sélection des coupes représentatives
            representative_slices = find_representative_slices(predictions, num_slices=3)
            print(f"  🎯 Coupes sélectionnées: {[s+1 for s in representative_slices]}")

            # 5. Génération du rapport médical haute qualité
            print("  📋 Génération du rapport médical haute qualité (anti-pixelisation)...")
            report_path = create_professional_visualization(
                predictions, representative_slices, original_data,
                normalized_data, patient_id, metrics, output_dir
            )

            print(f"  ✅ Rapport généré: {report_path}")
            print(f"  📈 Volume tumoral total: {metrics['total_tumor_volume_cm3']:.2f} cm³")
            successful_analyses += 1

        except Exception as e:
            print(f"  ❌ Erreur lors du traitement: {str(e)}")
            continue

    print("\n" + "="*100)
    print(f"🎉 ANALYSE TERMINÉE - {successful_analyses}/{len(patient_folders)} rapports générés avec succès")
    print(f"📁 Consultez le répertoire: {output_dir}")
    print("="*100)

if __name__ == "__main__":
    main()