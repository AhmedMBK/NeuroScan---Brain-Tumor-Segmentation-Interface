# 🚀 Guide d'Installation - API de Gestion des Patients

## 📋 Étapes d'Installation

### 1. Ouvrir le Terminal dans le Dossier Backend

**Option A : Via l'Explorateur Windows**
1. Naviguez vers le dossier `cerebloom-classify-87-main\backend`
2. Cliquez droit dans le dossier
3. Sélectionnez "Ouvrir dans le terminal" ou "Ouvrir PowerShell ici"

**Option B : Via le Terminal**
```bash
cd C:\Users\DELL\Desktop\cerebloom-classify-87-main\backend
```

### 2. Vérifier Python

```bash
python --version
```
ou
```bash
python3 --version
```

### 3. Installation avec Conda (Recommandé)

Si vous avez Conda installé :

```bash
# Créer l'environnement
conda create -n patients_api python=3.11 -y

# Activer l'environnement
conda activate patients_api

# Installer FastAPI et Uvicorn
conda install -c conda-forge fastapi uvicorn -y

# Installer Pydantic avec pip
pip install "pydantic[email]" email-validator
```

### 4. Installation avec Pip (Alternative)

Si vous n'avez pas Conda :

```bash
pip install fastapi uvicorn "pydantic[email]" email-validator
```

### 5. Vérification de l'Installation

```bash
python -c "import fastapi; print('✅ FastAPI OK')"
python -c "import uvicorn; print('✅ Uvicorn OK')"
python -c "import pydantic; print('✅ Pydantic OK')"
```

### 6. Démarrer l'API

```bash
python main_patients_api.py
```

### 7. Accéder à Swagger UI

Une fois le serveur démarré, ouvrez votre navigateur et allez à :

**🔗 http://localhost:8001/docs**

## 🛠️ Scripts Automatiques

### Installation Automatique
Double-cliquez sur `install_patients_api.bat` dans le dossier backend

### Démarrage Automatique
Double-cliquez sur `run_patients_api.bat` dans le dossier backend

## 🧪 Test de l'API

### Via Swagger UI
1. Allez sur http://localhost:8001/docs
2. Testez l'endpoint `/health` pour vérifier que l'API fonctionne
3. Explorez les endpoints `/patients`, `/scans`, `/treatments`, `/appointments`

### Endpoints de Test Rapide
- **Health Check** : `GET /health`
- **Liste des Patients** : `GET /patients`
- **Statistiques** : `GET /scans/statistics`

## 🔧 Résolution de Problèmes

### Problème : "python n'est pas reconnu"
**Solution** : Ajoutez Python au PATH ou utilisez le chemin complet

### Problème : "conda n'est pas reconnu"
**Solution** : 
1. Installez Anaconda ou Miniconda
2. Redémarrez le terminal
3. Ou utilisez l'installation avec pip

### Problème : "Module not found"
**Solution** : Réinstallez les dépendances
```bash
pip install --upgrade fastapi uvicorn pydantic email-validator
```

### Problème : "Port 8001 déjà utilisé"
**Solution** : Changez le port dans `main_patients_api.py` ligne finale :
```python
uvicorn.run("main_patients_api:app", host="0.0.0.0", port=8002, reload=True)
```

## 📊 Données de Test

L'API démarre automatiquement avec des données d'exemple :
- 2 patients
- 2 scans
- 2 traitements  
- 2 rendez-vous

Ces données permettent de tester immédiatement toutes les fonctionnalités via Swagger UI.

## 🎯 Prochaines Étapes

1. ✅ Installer les dépendances
2. ✅ Démarrer l'API
3. ✅ Tester avec Swagger UI
4. 🔄 Intégrer avec le frontend React
5. 🔄 Ajouter une base de données
6. 🔄 Implémenter l'authentification
