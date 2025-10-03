# 🚀 Démarrage Minimal - API Patients

## ⚡ Installation Ultra-Rapide

### 1. Ouvrir le Terminal dans Backend
- Naviguez vers le dossier `backend`
- Clic droit → "Ouvrir dans le terminal"

### 2. Installation Minimale (3 packages seulement)
```bash
pip install fastapi uvicorn pydantic
```

### 3. Démarrer l'API Simplifiée
```bash
python patients_api_simple.py
```

### 4. Tester dans Swagger
Ouvrez: **http://localhost:8001/docs**

## 🎯 Différences avec la Version Complète

### ✅ Version Simplifiée (patients_api_simple.py)
- **3 packages** seulement : `fastapi`, `uvicorn`, `pydantic`
- **Email simple** : pas de validation complexe
- **Modèles de base** : patients et scans uniquement
- **Installation rapide** : 30 secondes

### 🔧 Version Complète (main_patients_api.py)
- **5+ packages** : validation email, tests, etc.
- **Email validé** : avec `email-validator`
- **Modèles complets** : patients, scans, traitements, rendez-vous
- **Plus de fonctionnalités** : statistiques, filtres avancés

## 🧪 Tests Rapides dans Swagger

### 1. Health Check
- **GET** `/health`
- Résultat attendu: `{"status": "healthy", ...}`

### 2. Voir le Patient d'Exemple
- **GET** `/patients`
- Résultat: Jean Dupont avec toutes ses infos

### 3. Créer un Nouveau Patient
- **POST** `/patients`
- Exemple simple:

```json
{
  "first_name": "Test",
  "last_name": "Patient",
  "date_of_birth": "1990-01-01",
  "gender": "Male",
  "contact_number": "+33123456789",
  "email": "test@example.com",
  "address": "123 Test Street",
  "blood_type": "A+",
  "height": 175,
  "weight": 70,
  "emergency_contact": {
    "name": "Contact Test",
    "relationship": "Ami",
    "phone": "+33987654321"
  },
  "insurance": {
    "provider": "Test Insurance",
    "policy_number": "TEST123",
    "expiry_date": "2024-12-31"
  },
  "doctor": "Dr. Test",
  "medical_history": {
    "allergies": ["Aucune"],
    "chronic_conditions": [],
    "family_history": []
  },
  "notes": "Patient de test"
}
```

### 4. Voir les Scans
- **GET** `/scans`
- **GET** `/patients/patient-1/scans`

## 🔄 Passer à la Version Complète

Quand vous êtes prêt pour plus de fonctionnalités :

```bash
# Installer les dépendances supplémentaires
pip install email-validator

# Utiliser la version complète
python main_patients_api.py
```

## 🛠️ Résolution de Problèmes

### "python n'est pas reconnu"
```bash
# Vérifiez Python
python --version
# ou
python3 --version
```

### "Module not found"
```bash
# Réinstallez
pip install --upgrade fastapi uvicorn pydantic
```

### Port déjà utilisé
Changez le port dans `patients_api_simple.py` :
```python
uvicorn.run("patients_api_simple:app", port=8002)
```

---

**🎯 Objectif** : Tester rapidement l'API sans complications d'installation !

**⏱️ Temps total** : 2-3 minutes de l'installation au test dans Swagger
