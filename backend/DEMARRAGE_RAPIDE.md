# 🚀 Démarrage Rapide - API Patients

## 📂 Étape 1: Ouvrir le Terminal dans Backend

### Windows (Méthode Recommandée)
1. Ouvrez l'Explorateur Windows
2. Naviguez vers: `C:\Users\DELL\Desktop\cerebloom-classify-87-main\backend`
3. **Clic droit** dans le dossier backend
4. Sélectionnez **"Ouvrir dans le terminal"** ou **"Ouvrir PowerShell ici"**

### Alternative
```bash
cd C:\Users\DELL\Desktop\cerebloom-classify-87-main\backend
```

## 🔧 Étape 2: Tester l'Environnement

```bash
python test_imports.py
```

Ce script va vérifier:
- ✅ Si Python fonctionne
- ✅ Si les fichiers sont présents
- ❌ Quelles dépendances manquent

## 📦 Étape 3: Installer les Dépendances

### Option A: Avec Conda (Recommandé)
```bash
conda install -c conda-forge fastapi uvicorn -y
pip install "pydantic[email]" email-validator
```

### Option B: Avec Pip
```bash
pip install fastapi uvicorn "pydantic[email]" email-validator
```

### Option C: Script Automatique
```bash
# PowerShell
.\install_patients_api.ps1

# Ou Batch
install_patients_api.bat
```

## 🚀 Étape 4: Démarrer l'API

```bash
python main_patients_api.py
```

## 🌐 Étape 5: Tester avec Swagger

1. Ouvrez votre navigateur
2. Allez sur: **http://localhost:8001/docs**
3. Testez les endpoints!

## 🧪 Tests Rapides dans Swagger

### 1. Health Check
- **GET** `/health`
- Cliquez sur "Try it out" → "Execute"
- Vous devriez voir: `{"status": "healthy", ...}`

### 2. Liste des Patients
- **GET** `/patients`
- Cliquez sur "Try it out" → "Execute"
- Vous devriez voir 2 patients d'exemple

### 3. Créer un Patient
- **POST** `/patients`
- Cliquez sur "Try it out"
- Utilisez cet exemple:

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
    "allergies": [],
    "chronic_conditions": [],
    "past_surgeries": [],
    "family_history": []
  },
  "notes": "Patient de test"
}
```

## 🔍 Endpoints Principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Vérification de l'API |
| `/patients` | GET | Liste des patients |
| `/patients` | POST | Créer un patient |
| `/patients/{id}` | GET | Détails d'un patient |
| `/scans` | GET | Liste des examens |
| `/treatments` | GET | Liste des traitements |
| `/appointments` | GET | Liste des rendez-vous |

## 🛠️ Résolution de Problèmes

### Problème: "python n'est pas reconnu"
**Solution**: Installez Python ou ajoutez-le au PATH

### Problème: "Module not found"
**Solution**: Réinstallez les dépendances
```bash
pip install --upgrade fastapi uvicorn pydantic email-validator
```

### Problème: "Port 8001 déjà utilisé"
**Solution**: Changez le port dans `main_patients_api.py`:
```python
uvicorn.run("main_patients_api:app", port=8002)
```

## 📊 Données de Test

L'API démarre avec:
- 👥 2 patients (Jean Dupont, Marie Martin)
- 🔬 2 examens IRM
- 💊 2 traitements actifs
- 📅 2 rendez-vous programmés

## 🎯 Prochaines Étapes

1. ✅ Tester tous les endpoints dans Swagger
2. 🔄 Intégrer avec le frontend React
3. 🗄️ Ajouter une vraie base de données
4. 🔐 Implémenter l'authentification

---

**🆘 Besoin d'aide?** Consultez `GUIDE_INSTALLATION.md` pour plus de détails.
