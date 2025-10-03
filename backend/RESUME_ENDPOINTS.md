# 📋 Résumé des Endpoints - API Utilisateurs et Médecins

## 🚀 **Démarrage Rapide**
```bash
python main_users_api.py
```
**Swagger UI** : http://localhost:8002/docs

---

## 🔐 **AUTHENTIFICATION**

| Méthode | Endpoint | Description | Auth Required |
|---------|----------|-------------|---------------|
| POST | `/auth/login` | Connexion | ❌ |
| POST | `/auth/register` | Inscription | ❌ |
| GET | `/auth/me` | Profil actuel | ✅ |
| POST | `/auth/logout` | Déconnexion | ✅ |

**Comptes de test :**
- `admin` / `admin123` (Administrateur)
- `dr.martin` / `doctor123` (Neurologue)
- `dr.dubois` / `onco123` (Oncologue)
- `nurse.claire` / `nurse123` (Infirmière)

---

## 👥 **GESTION DES UTILISATEURS**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| GET | `/users` | Liste utilisateurs | Admin |
| GET | `/users/{id}` | Détails utilisateur | Admin/Self |
| PUT | `/users/{id}` | Modifier utilisateur | Admin/Self |
| DELETE | `/users/{id}` | Supprimer utilisateur | Admin |

**Filtres disponibles :**
- `?role=Doctor` - Par rôle
- `?status=Active` - Par statut
- `?search=martin` - Recherche texte
- `?skip=0&limit=100` - Pagination

---

## 🩺 **GESTION DES MÉDECINS**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| GET | `/doctors` | Liste publique | Public |
| GET | `/doctors/{id}` | Détails médecin | Auth |
| GET | `/doctors/public/{id}` | Profil public | Public |
| POST | `/doctors` | Créer profil | Admin |
| PUT | `/doctors/{id}` | Modifier profil | Admin/Self |
| DELETE | `/doctors/{id}` | Supprimer profil | Admin |

**Endpoints spécialisés :**
- GET `/doctors/by-specialty/{specialty}` - Par spécialité
- GET `/doctors/{id}/schedule` - Emploi du temps
- GET `/doctors/statistics` - Statistiques

**Spécialités disponibles :**
- `Neurology` - Neurologie
- `Oncology` - Oncologie
- `Radiology` - Radiologie
- `Neurosurgery` - Neurochirurgie
- `General Medicine` - Médecine générale
- `Psychiatry` - Psychiatrie
- `Anesthesiology` - Anesthésie

---

## 📊 **STATISTIQUES ET SANTÉ**

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| GET | `/health` | État de l'API | Public |
| GET | `/` | Info API | Public |
| GET | `/doctors/statistics` | Stats médecins | Reports |

---

## 🎯 **WORKFLOW DE TEST RECOMMANDÉ**

### **1. Tests de Base (Public)**
```
GET /health
GET /
GET /doctors
GET /doctors/public/{id}
GET /doctors/by-specialty/Neurology
```

### **2. Tests d'Authentification**
```
POST /auth/login (admin/admin123)
GET /auth/me
POST /auth/logout
```

### **3. Tests Admin**
```
POST /auth/login (admin)
GET /users
POST /auth/register (nouveau user)
POST /doctors (nouveau médecin)
GET /doctors/statistics
```

### **4. Tests Médecin**
```
POST /auth/login (dr.martin)
GET /auth/me
PUT /doctors/{id} (son profil)
```

### **5. Tests de Recherche**
```
GET /users?search=martin
GET /doctors?specialty=Neurology
GET /doctors?available_only=true
```

---

## 🔑 **AUTHENTIFICATION DANS SWAGGER**

1. **Se connecter :**
   - POST `/auth/login` avec username/password
   - Copier le `access_token`

2. **Autoriser :**
   - Cliquer "Authorize" en haut à droite
   - Entrer : `Bearer VOTRE_TOKEN`
   - Cliquer "Authorize"

3. **Tester :**
   - Maintenant tous les endpoints protégés sont accessibles

---

## 📝 **EXEMPLES DE BODY RAPIDES**

### **Connexion Admin :**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

### **Créer Utilisateur :**
```json
{
  "first_name": "Test",
  "last_name": "User",
  "email": "test@example.com",
  "phone": "+33123456789",
  "gender": "Male",
  "date_of_birth": "1990-01-01",
  "address": "123 Test Street",
  "role": "Doctor",
  "status": "Active",
  "is_verified": true,
  "username": "test.user",
  "password": "test123",
  "confirm_password": "test123"
}
```

### **Créer Médecin :**
```json
{
  "user_id": "COPIER_ID_UTILISATEUR",
  "license_number": "FR-TEST-2024-001",
  "specialty": "General Medicine",
  "sub_specialties": [],
  "years_of_experience": 5,
  "education": [
    {
      "degree": "Doctorat en Médecine",
      "institution": "Université Test",
      "graduation_year": "2019",
      "country": "France"
    }
  ],
  "certifications": [],
  "languages_spoken": ["Français"],
  "consultation_fee": "80€",
  "schedule": [
    {
      "day_of_week": "Lundi",
      "start_time": "09:00",
      "end_time": "17:00",
      "is_available": true,
      "notes": "Consultations"
    }
  ],
  "status": "Active",
  "bio": "Médecin test",
  "rating": 4.5,
  "total_reviews": 10
}
```

---

## ⚠️ **CODES D'ERREUR COURANTS**

- **400** : Données invalides (email déjà utilisé, mots de passe différents)
- **401** : Non authentifié (token manquant/expiré)
- **403** : Permissions insuffisantes
- **404** : Ressource non trouvée
- **423** : Compte verrouillé (trop de tentatives)

---

## 🎯 **POINTS CLÉS**

- **Tokens** expirent après 30 minutes
- **IDs** sont des UUIDs générés automatiquement
- **Permissions** basées sur les rôles (RBAC)
- **Validation** stricte des formats (email, téléphone, dates)
- **Recherche** insensible à la casse
- **Pagination** par défaut : skip=0, limit=100

---

**📄 Guide complet :** `EXEMPLES_TESTS_SWAGGER.md`
**🚀 Démarrage rapide :** `DEMARRAGE_TESTS.bat`
