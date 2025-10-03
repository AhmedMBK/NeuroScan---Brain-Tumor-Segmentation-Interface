# 🧠 CereBloom - Backend Complet

## 📋 Vue d'Ensemble

**CereBloom** est une application de cabinet médical spécialisée dans la segmentation automatique de tumeurs cérébrales utilisant votre modèle U-Net Kaggle. Le système intègre une architecture complète basée sur le diagramme UML Relations et Flux de Données.

## 🎯 Fonctionnalités Principales

### 🔐 **Système d'Authentification**
- 3 rôles utilisateur : **Admin**, **Doctor**, **Secretary**
- Authentification JWT avec refresh tokens
- Gestion des permissions granulaires
- Sessions utilisateur sécurisées

### 🏥 **Gestion Patients**
- Dossiers patients complets
- Historique médical
- Consultations et diagnostics
- Assignation aux médecins

### 🖼️ **Images Médicales**
- Support des formats NIfTI (.nii, .nii.gz)
- 4 modalités : **T1**, **T1CE**, **T2**, **FLAIR**
- Séries d'images groupées
- Métadonnées DICOM

### 🧠 **IA Segmentation (CŒUR)**
- **Intégration de votre modèle U-Net Kaggle**
- Segmentation automatique en arrière-plan
- 3 types de tumeurs détectées :
  - 🔴 **Noyau nécrotique** (rouge)
  - 🟢 **Œdème péritumoral** (vert)
  - 🔵 **Tumeur rehaussée** (bleu)
- Analyse volumétrique précise en cm³
- Comparaisons temporelles

### 💊 **Traitements**
- Prescriptions médicamenteuses
- Suivi des traitements
- Historique thérapeutique

### 📅 **Rendez-vous**
- Planification des consultations
- Rappels automatiques (Email/SMS)
- Gestion des annulations

### 📄 **Rapports**
- Templates personnalisables
- Rapports de segmentation illustrés
- Export des données

## 🏗️ Architecture

### **Diagramme UML Relations et Flux de Données**
L'architecture suit le diagramme UML avec :
- **Users** au centre du système
- **AISegmentation** comme cœur de l'application
- Relations 1:1, 1:N optimisées
- Flux de données cohérent

### **Technologies Utilisées**
- **FastAPI** : Framework web moderne
- **SQLAlchemy** : ORM avec support async
- **SQLite** : Base de données (configurable)
- **TensorFlow** : Pour votre modèle U-Net
- **JWT** : Authentification sécurisée
- **Pydantic** : Validation des données

## 🚀 Installation et Démarrage

### **Prérequis**
- Python 3.10+
- Votre modèle U-Net Kaggle (`my_model.h5`)

### **Installation Rapide**
```bash
# 1. Cloner et naviguer
cd backend

# 2. Lancer le script de démarrage
run_cerebloom.bat

# 3. Accéder à l'application
# API: http://localhost:8000
# Documentation: http://localhost:8000/docs
```

### **Installation Manuelle**
```bash
# 1. Environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Dépendances
pip install -r requirements_cerebloom.txt

# 3. Configuration
cp .env.example .env
# Modifier .env selon vos besoins

# 4. Modèle IA
# Copier votre my_model.h5 dans models/

# 5. Démarrage
python cerebloom_main.py
```

## 🔧 Configuration

### **Variables d'Environnement (.env)**
```env
# Sécurité
SECRET_KEY=votre-clé-secrète-unique

# Base de données
DATABASE_URL=sqlite+aiosqlite:///./cerebloom.db

# IA
AI_MODEL_PATH=models/my_model.h5
AI_CONFIDENCE_THRESHOLD=0.7

# Cabinet
CABINET_NAME=Votre Cabinet Médical
```

### **Votre Modèle U-Net**
Placez votre modèle Kaggle dans :
```
backend/models/my_model.h5
```

Le système charge automatiquement vos métriques personnalisées :
- `dice_coef`
- `precision`
- `sensitivity`
- `specificity`
- `dice_coef_necrotic`
- `dice_coef_edema`
- `dice_coef_enhancing`

## 👥 Rôles et Permissions

### 🔐 **ADMIN**
- Gestion complète des utilisateurs
- Création de templates de rapports
- Accès aux métriques globales
- Export des données

### 👨‍⚕️ **DOCTOR**
- Gestion de ses patients
- **Validation des segmentations IA**
- Prescriptions et traitements
- Création de rapports médicaux
- Analyse de l'évolution volumétrique

### 👩‍💼 **SECRETARY**
- Création de dossiers patients
- **Upload d'images médicales**
- Gestion des rendez-vous
- Lancement des segmentations

## 🧠 Flux de Segmentation IA

### **1. Upload des Images**
```
Secrétaire → Upload 4 images (T1, T1CE, T2, FLAIR)
```

### **2. Création de Série**
```
Images → ImageSeries (groupement)
```

### **3. Lancement Segmentation**
```
Doctor/Secretary → AISegmentation (votre modèle U-Net)
```

### **4. Traitement Automatique**
```
Modèle U-Net → TumorSegments + VolumetricAnalysis
```

### **5. Validation Médicale**
```
Doctor → Validation + SegmentationReport
```

## 📊 API Endpoints

### **Authentification**
- `POST /api/v1/auth/login` - Connexion
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Infos utilisateur

### **IA Segmentation (CŒUR)**
- `POST /api/v1/segmentation/create` - Nouvelle segmentation
- `GET /api/v1/segmentation/status/{id}` - Statut
- `GET /api/v1/segmentation/segments/{id}` - Segments tumoraux
- `POST /api/v1/segmentation/validate/{id}` - Validation

### **Patients**
- `POST /api/v1/patients` - Créer patient
- `GET /api/v1/patients/{id}` - Détails patient
- `PUT /api/v1/patients/{id}` - Modifier patient

### **Images Médicales**
- `POST /api/v1/images/upload` - Upload image
- `POST /api/v1/images/series` - Créer série
- `GET /api/v1/images/patient/{id}` - Images patient

## 🔒 Sécurité

### **Authentification**
- JWT avec expiration
- Refresh tokens
- Verrouillage après tentatives échouées
- Sessions sécurisées

### **Permissions**
- Contrôle d'accès granulaire
- Vérification par endpoint
- Isolation des données par rôle

### **Données**
- Validation Pydantic
- Sanitisation des entrées
- Logs de sécurité

## 📈 Monitoring et Logs

### **Logs Structurés**
```
logs/cerebloom.log
```

### **Métriques Disponibles**
- Nombre de segmentations
- Volumes moyens par type
- Performance du modèle
- Activité utilisateurs

## 🧪 Tests

```bash
# Tests unitaires
pytest

# Tests avec couverture
pytest --cov=.

# Tests d'intégration
pytest tests/integration/
```

## 🚀 Déploiement Production

### **Configuration Production**
```env
DEBUG=false
SECRET_KEY=clé-très-sécurisée
DATABASE_URL=postgresql://...
```

### **Docker (Optionnel)**
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements_cerebloom.txt
CMD ["python", "cerebloom_main.py"]
```

## 🆘 Support et Dépannage

### **Problèmes Courants**

**Modèle non trouvé :**
```
Copiez votre my_model.h5 dans backend/models/
```

**Erreur de dépendances :**
```bash
pip install --upgrade -r requirements_cerebloom.txt
```

**Base de données :**
```bash
# Réinitialiser la DB
rm cerebloom.db
python cerebloom_main.py
```

### **Logs de Debug**
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📞 Contact

- **Email** : support@cerebloom.com
- **Documentation** : http://localhost:8000/docs
- **Logs** : `logs/cerebloom.log`

---

## 🎯 Compte Admin par Défaut

**Email** : `admin@cerebloom.com`  
**Mot de passe** : `admin123`

⚠️ **Changez ce mot de passe en production !**

---

*CereBloom v2.0.0 - Intégration complète de votre modèle U-Net Kaggle* 🧠
