#!/usr/bin/env python3
"""
🚀 Serveur CereBloom Simplifié
Version minimale pour tester votre modèle professionnel
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import os
from pathlib import Path

# Créer l'application FastAPI
app = FastAPI(
    title="🧠 CereBloom API - Modèle Professionnel",
    description="API simplifiée pour tester votre modèle test_brain_tumor_segmentationFinal.py",
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

@app.get("/")
async def root():
    """Page d'accueil"""
    return {
        "message": "🧠 CereBloom API - Votre Modèle Professionnel",
        "description": "Serveur simplifié pour tester test_brain_tumor_segmentationFinal.py",
        "endpoints": {
            "health": "/health",
            "test_model": "/test-model",
            "segmentation": "/segment/{patient_id}",
            "docs": "/docs"
        },
        "patient_test": "stringd5f01d3b-b54b-43a2-ba3c-0b12c797affc"
    }

@app.get("/health")
async def health_check():
    """Vérification de santé"""
    
    # Vérifier le modèle
    model_path = Path("models/my_model.h5")
    model_status = "found" if model_path.exists() else "missing"
    
    # Vérifier TensorFlow
    try:
        import tensorflow as tf
        tf_status = f"available ({tf.__version__})"
    except ImportError:
        tf_status = "not available"
    
    # Vérifier le script professionnel
    script_path = Path("test_brain_tumor_segmentationFinal.py")
    script_status = "found" if script_path.exists() else "missing"
    
    return {
        "status": "healthy",
        "model": model_status,
        "tensorflow": tf_status,
        "professional_script": script_status,
        "ready_for_segmentation": model_status == "found" and script_status == "found"
    }

@app.get("/test-model")
async def test_model():
    """Test rapide du modèle"""
    try:
        # Importer votre script
        from test_brain_tumor_segmentationFinal import load_model_with_custom_objects
        
        model_path = "models/my_model.h5"
        if not os.path.exists(model_path):
            return {
                "status": "error",
                "message": "Modèle non trouvé",
                "path": model_path
            }
        
        # Tenter de charger le modèle
        model = load_model_with_custom_objects(model_path)
        
        if model is not None:
            return {
                "status": "success",
                "message": "Modèle chargé avec succès",
                "model_info": {
                    "path": model_path,
                    "input_shape": str(model.input_shape) if hasattr(model, 'input_shape') else "N/A",
                    "output_shape": str(model.output_shape) if hasattr(model, 'output_shape') else "N/A"
                }
            }
        else:
            return {
                "status": "error",
                "message": "Échec du chargement du modèle"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors du test : {str(e)}"
        }

@app.post("/segment/{patient_id}")
async def segment_patient(patient_id: str):
    """Lance la segmentation avec votre modèle professionnel"""
    try:
        print(f"🧠 Lancement segmentation pour patient: {patient_id}")
        
        # Importer votre fonction
        from test_brain_tumor_segmentationFinal import process_patient_with_professional_model
        
        # Créer le dossier de sortie
        output_dir = f"uploads/segmentation_results/{patient_id}_professional"
        os.makedirs(output_dir, exist_ok=True)
        
        # Lancer votre modèle professionnel
        result = await process_patient_with_professional_model(
            patient_id=patient_id,
            output_dir=output_dir
        )
        
        if result["success"]:
            return {
                "status": "completed",
                "message": "Segmentation réussie avec votre modèle professionnel",
                "patient_id": patient_id,
                "results": {
                    "total_volume": result["metrics"]["total_volume"],
                    "modalities_used": result["modalities_used"],
                    "representative_slices": result["representative_slices"],
                    "report_path": result["report_path"]
                },
                "output_directory": output_dir
            }
        else:
            return {
                "status": "failed",
                "message": "Échec de la segmentation",
                "error": result.get("error", "Erreur inconnue")
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la segmentation : {str(e)}"
        }

@app.get("/results")
async def list_results():
    """Liste tous les résultats de segmentation"""
    try:
        results_dir = Path("results_medical")
        segmentation_dir = Path("uploads/segmentation_results")
        
        results = {
            "medical_reports": [],
            "segmentation_results": []
        }
        
        # Rapports médicaux
        if results_dir.exists():
            for report in results_dir.glob("*.png"):
                size_mb = report.stat().st_size / (1024 * 1024)
                results["medical_reports"].append({
                    "filename": report.name,
                    "size_mb": round(size_mb, 2),
                    "path": str(report.absolute())
                })
        
        # Résultats de segmentation
        if segmentation_dir.exists():
            for folder in segmentation_dir.iterdir():
                if folder.is_dir():
                    files = list(folder.glob("*"))
                    results["segmentation_results"].append({
                        "segmentation_id": folder.name,
                        "files_count": len(files),
                        "path": str(folder.absolute())
                    })
        
        return results
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la récupération des résultats : {str(e)}"
        }

if __name__ == "__main__":
    print("🧠 CEREBLOOM - SERVEUR SIMPLIFIÉ")
    print("=" * 50)
    print("🌐 Swagger UI : http://localhost:8000/docs")
    print("🔗 API Health : http://localhost:8000/health")
    print("🧪 Test Modèle : http://localhost:8000/test-model")
    print("🎯 Segmentation : POST http://localhost:8000/segment/{patient_id}")
    print("=" * 50)
    
    # Créer les dossiers nécessaires
    os.makedirs("uploads/segmentation_results", exist_ok=True)
    os.makedirs("results_medical", exist_ok=True)
    
    # Démarrer le serveur
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
