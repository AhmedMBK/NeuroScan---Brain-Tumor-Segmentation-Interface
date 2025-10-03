"""
Créer un modèle factice pour tester CereBloom
En attendant votre vrai modèle U-Net Kaggle
"""

import os
import numpy as np

# Créer un fichier factice pour éviter l'erreur de modèle manquant
dummy_model_content = """
# Modèle factice pour CereBloom
# Remplacez ce fichier par votre vrai modèle my_model.h5 de Kaggle

Ce fichier est un placeholder.
Copiez votre modèle U-Net Kaggle ici : models/my_model.h5
"""

os.makedirs("models", exist_ok=True)

with open("models/model_placeholder.txt", "w") as f:
    f.write(dummy_model_content)

print("✅ Placeholder créé dans models/")
print("📝 Copiez votre modèle my_model.h5 dans le dossier models/")
