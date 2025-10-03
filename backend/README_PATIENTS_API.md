# API de Gestion des Patients - CereBloom

## 📋 Description

API FastAPI complète pour la gestion des patients et de leurs examens médicaux dans le cadre du projet CereBloom. Cette API permet de gérer :

- **Patients** : Informations complètes, historique médical, contacts d'urgence
- **Examens** : Scans IRM, CT, PET, X-Ray avec résultats de diagnostic
- **Traitements** : Médicaments, chirurgies, radiothérapie, chimiothérapie
- **Rendez-vous** : Planification et suivi des consultations médicales

## 🚀 Installation

### Prérequis
- Python 3.11+
- Conda (Anaconda ou Miniconda)

### Installation automatique
```bash
# Exécuter le script d'installation
install_patients_api.bat
```

### Installation manuelle
```bash
# Créer l'environnement Conda
conda create -n patients_api python=3.11 -y

# Activer l'environnement
conda activate patients_api

# Installer les dépendances
pip install -r requirements_patients.txt
```

## 🏃‍♂️ Démarrage

### Démarrage automatique
```bash
# Exécuter le script de démarrage
run_patients_api.bat
```

### Démarrage manuel
```bash
# Activer l'environnement
conda activate patients_api

# Démarrer l'API
python main_patients_api.py
```

L'API sera disponible sur :
- **API** : http://localhost:8001
- **Documentation** : http://localhost:8001/docs
- **ReDoc** : http://localhost:8001/redoc

## 📚 Endpoints Principaux

### Patients
- `GET /patients` - Liste des patients avec filtres
- `POST /patients` - Créer un nouveau patient
- `GET /patients/{id}` - Détails d'un patient
- `PUT /patients/{id}` - Modifier un patient
- `DELETE /patients/{id}` - Supprimer un patient
- `GET /patients/{id}/summary` - Résumé complet du patient

### Examens (Scans)
- `GET /scans` - Liste des examens avec filtres
- `POST /scans` - Créer un nouvel examen
- `GET /scans/{id}` - Détails d'un examen
- `PUT /scans/{id}` - Modifier un examen
- `DELETE /scans/{id}` - Supprimer un examen
- `GET /patients/{id}/scans` - Examens d'un patient
- `GET /patients/{id}/scans/latest` - Dernier examen d'un patient

### Traitements
- `GET /treatments` - Liste des traitements avec filtres
- `POST /treatments` - Créer un nouveau traitement
- `GET /treatments/{id}` - Détails d'un traitement
- `PUT /treatments/{id}` - Modifier un traitement
- `DELETE /treatments/{id}` - Supprimer un traitement
- `GET /patients/{id}/treatments` - Traitements d'un patient
- `GET /patients/{id}/treatments/active` - Traitements actifs d'un patient

### Rendez-vous
- `GET /appointments` - Liste des rendez-vous avec filtres
- `POST /appointments` - Créer un nouveau rendez-vous
- `GET /appointments/{id}` - Détails d'un rendez-vous
- `PUT /appointments/{id}` - Modifier un rendez-vous
- `DELETE /appointments/{id}` - Supprimer un rendez-vous
- `GET /patients/{id}/appointments` - Rendez-vous d'un patient
- `GET /appointments/today` - Rendez-vous d'aujourd'hui
- `GET /appointments/upcoming` - Prochains rendez-vous

### Statistiques
- `GET /scans/statistics` - Statistiques des examens
- `GET /treatments/statistics` - Statistiques des traitements
- `GET /appointments/statistics` - Statistiques des rendez-vous

## 🧪 Tests

### Exécution automatique
```bash
test_patients_api.bat
```

### Exécution manuelle
```bash
conda activate patients_api
python test_patients_api.py
```

## 📊 Modèles de Données

### Patient
```json
{
  "id": "string",
  "first_name": "string",
  "last_name": "string",
  "date_of_birth": "YYYY-MM-DD",
  "gender": "Male|Female|Other",
  "contact_number": "string",
  "email": "email@example.com",
  "address": "string",
  "blood_type": "A+|A-|B+|B-|AB+|AB-|O+|O-",
  "height": 180,
  "weight": 75.5,
  "emergency_contact": {
    "name": "string",
    "relationship": "string",
    "phone": "string"
  },
  "insurance": {
    "provider": "string",
    "policy_number": "string",
    "expiry_date": "YYYY-MM-DD"
  },
  "doctor": "string",
  "medical_history": {
    "allergies": ["string"],
    "chronic_conditions": ["string"],
    "past_surgeries": [
      {
        "procedure": "string",
        "date": "YYYY-MM-DD",
        "notes": "string"
      }
    ],
    "family_history": ["string"]
  },
  "notes": "string"
}
```

### Scan
```json
{
  "id": "string",
  "patient_id": "string",
  "date": "YYYY-MM-DD",
  "type": "MRI|CT|PET|X-Ray",
  "body_part": "string",
  "image_url": "string",
  "result": {
    "diagnosis": "string",
    "tumor_type": "string",
    "tumor_size": "string",
    "tumor_location": "string",
    "malignant": true,
    "notes": "string"
  },
  "doctor": "string",
  "facility": "string",
  "status": "Completed|Pending|Processing|Failed"
}
```

## 🔧 Fonctionnalités

### Filtres et Recherche
- **Patients** : Recherche par nom, email, téléphone, filtrage par médecin, genre
- **Examens** : Filtrage par patient, type, statut, médecin, période
- **Traitements** : Filtrage par patient, type, statut, efficacité
- **Rendez-vous** : Filtrage par patient, statut, médecin, période

### Pagination
Tous les endpoints de liste supportent la pagination :
- `skip` : Nombre d'éléments à ignorer (défaut: 0)
- `limit` : Nombre maximum d'éléments (défaut: 100, max: 1000)

### Validation
- Validation automatique des données avec Pydantic
- Validation des emails
- Validation des dates
- Validation des types énumérés

### Métadonnées Automatiques
- Mise à jour automatique des dates de dernier scan et prochain rendez-vous
- Calcul automatique de l'âge des patients
- Horodatage automatique (created_at, updated_at)

## 🔗 Intégration Frontend

Cette API est conçue pour s'intégrer parfaitement avec le frontend React du projet CereBloom. Les modèles de données correspondent exactement aux interfaces TypeScript utilisées dans le frontend.

## 📝 Notes de Développement

- **Stockage** : Actuellement en mémoire (à remplacer par une base de données en production)
- **Authentification** : À implémenter selon les besoins
- **CORS** : Configuré pour accepter toutes les origines (à restreindre en production)
- **Logs** : Logs basiques avec uvicorn (à améliorer pour la production)

## 🚀 Prochaines Étapes

1. Intégration avec une base de données (PostgreSQL/MongoDB)
2. Système d'authentification et d'autorisation
3. Upload et gestion des fichiers d'images
4. Notifications et alertes
5. Rapports et exports
6. Cache et optimisations de performance
