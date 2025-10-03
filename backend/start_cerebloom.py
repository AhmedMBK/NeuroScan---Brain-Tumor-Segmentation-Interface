#!/usr/bin/env python3
"""
🚀 Lanceur CereBloom Backend
Script simple pour démarrer le serveur avec votre modèle professionnel
"""

import uvicorn
import sys
import os
from pathlib import Path

def start_cerebloom():
    """Démarre le serveur CereBloom"""
    print("🧠 CEREBLOOM - DÉMARRAGE DU BACKEND")
    print("=" * 60)
    
    # Vérifications préliminaires
    print("🔍 Vérifications...")
    
    # 1. Vérifier le modèle
    model_path = Path("models/my_model.h5")
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✅ Modèle U-Net : {model_path} ({size_mb:.1f} MB)")
    else:
        print(f"⚠️ Modèle non trouvé : {model_path}")
    
    # 2. Vérifier TensorFlow
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow : {tf.__version__}")
    except ImportError:
        print("⚠️ TensorFlow : Mode simulation")
    
    # 3. Vérifier les dossiers
    required_dirs = [
        "uploads/medical_images",
        "uploads/segmentation_results", 
        "uploads/reports",
        "models",
        "results_medical"
    ]
    
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Dossier : {dir_path}")
    
    print()
    print("🚀 DÉMARRAGE DU SERVEUR...")
    print("=" * 60)
    print("🌐 URL Swagger : http://localhost:8000/docs")
    print("🔗 API Health : http://localhost:8000/health")
    print("📋 Endpoint Segmentation : POST /api/v1/segmentation/process-patient/{patient_id}")
    print("🆔 Patient de test : stringd5f01d3b-b54b-43a2-ba3c-0b12c797affc")
    print("=" * 60)
    
    try:
        # Démarrer le serveur
        uvicorn.run(
            "cerebloom_main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Erreur démarrage : {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_cerebloom()
