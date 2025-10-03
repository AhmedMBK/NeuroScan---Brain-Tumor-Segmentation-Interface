# 🧪 Tests Swagger Complets - API Utilisateurs et Médecins

## 🚀 Démarrage de l'API

```bash
# Dans le dossier backend
python main_users_api.py
```

**URL Swagger** : http://localhost:8002/docs

---

## 🔐 **1. AUTHENTIFICATION**

### **POST /auth/register** - Inscription d'un utilisateur

```json
{
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean.dupont@test.com",
  "phone": "+33123456789",
  "gender": "Male",
  "date_of_birth": "1985-03-15",
  "address": "123 Rue de Test, 75001 Paris",
  "role": "Doctor",
  "status": "Active",
  "is_verified": true,
  "profile_picture": null,
  "notes": "Nouveau médecin",
  "username": "jean.dupont",
  "password": "motdepasse123",
  "confirm_password": "motdepasse123"
}
```

### **POST /auth/login** - Connexion

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Autres comptes de test :**
```json
{
  "username": "dr.martin",
  "password": "doctor123"
}
```

```json
{
  "username": "dr.dubois",
  "password": "onco123"
}
```

```json
{
  "username": "nurse.claire",
  "password": "nurse123"
}
```

### **GET /auth/me** - Profil utilisateur actuel
*Pas de body - Nécessite un token d'authentification*

### **POST /auth/logout** - Déconnexion
*Pas de body - Nécessite un token d'authentification*

---

## 👥 **2. GESTION DES UTILISATEURS**

### **GET /users** - Liste des utilisateurs
*Pas de body - Paramètres de requête optionnels :*
- `skip`: 0
- `limit`: 100
- `role`: "Doctor" | "Nurse" | "Admin" | "Technician" | "Receptionist"
- `status`: "Active" | "Inactive" | "Suspended" | "Pending Verification"
- `search`: "martin"

### **GET /users/{user_id}** - Détails d'un utilisateur
*Pas de body - Remplacer {user_id} par un ID réel*

### **PUT /users/{user_id}** - Modifier un utilisateur

```json
{
  "first_name": "Jean-Pierre",
  "last_name": "Dupont-Martin",
  "email": "jp.dupont@test.com",
  "phone": "+33123456790",
  "gender": "Male",
  "date_of_birth": "1985-03-15",
  "address": "456 Avenue Modifiée, 75002 Paris",
  "role": "Doctor",
  "status": "Active",
  "department": "Neurologie",
  "employee_id": "DOC003",
  "profile_picture": "https://example.com/photo.jpg",
  "notes": "Informations mises à jour"
}
```

### **DELETE /users/{user_id}** - Supprimer un utilisateur
*Pas de body - Remplacer {user_id} par un ID réel*

---

## 🩺 **3. GESTION DES MÉDECINS**

### **POST /doctors** - Créer un profil médecin

```json
{
  "user_id": "USER_ID_ICI",
  "license_number": "FR-NEU-2024-001",
  "specialty": "Neurology",
  "sub_specialties": ["Neurosurgery"],
  "years_of_experience": 15,
  "education": [
    {
      "degree": "Doctorat en Médecine",
      "institution": "Université Paris Descartes",
      "graduation_year": "2009",
      "country": "France"
    },
    {
      "degree": "Spécialisation en Neurologie",
      "institution": "Hôpital Pitié-Salpêtrière",
      "graduation_year": "2014",
      "country": "France"
    }
  ],
  "certifications": [
    {
      "name": "Certification Européenne de Neurologie",
      "issuing_body": "European Board of Neurology",
      "issue_date": "2014-06-15",
      "expiry_date": "2024-06-15",
      "certificate_number": "EBN-2014-5678",
      "is_active": true
    }
  ],
  "languages_spoken": ["Français", "Anglais", "Espagnol"],
  "consultation_fee": "180€",
  "schedule": [
    {
      "day_of_week": "Lundi",
      "start_time": "09:00",
      "end_time": "17:00",
      "is_available": true,
      "notes": "Consultations générales"
    },
    {
      "day_of_week": "Mardi",
      "start_time": "09:00",
      "end_time": "17:00",
      "is_available": true,
      "notes": "Consultations spécialisées"
    },
    {
      "day_of_week": "Mercredi",
      "start_time": "09:00",
      "end_time": "15:00",
      "is_available": true,
      "notes": "Chirurgies"
    }
  ],
  "status": "Active",
  "bio": "Dr. Jean Dupont est un neurologue expérimenté spécialisé dans le traitement des tumeurs cérébrales. Il a 15 ans d'expérience et est reconnu pour son expertise en neurochirurgie.",
  "rating": 4.7,
  "total_reviews": 89
}
```

### **GET /doctors** - Liste publique des médecins
*Pas de body - Paramètres de requête optionnels :*
- `skip`: 0
- `limit`: 100
- `specialty`: "Neurology" | "Oncology" | "Radiology" | "Neurosurgery" | "General Medicine" | "Psychiatry" | "Anesthesiology"
- `status`: "Active" | "On Leave" | "Retired" | "Suspended"
- `search`: "martin"
- `available_only`: true

### **GET /doctors/{doctor_id}** - Détails d'un médecin
*Pas de body - Remplacer {doctor_id} par un ID réel*

### **GET /doctors/public/{doctor_id}** - Profil public d'un médecin
*Pas de body - Remplacer {doctor_id} par un ID réel*

### **PUT /doctors/{doctor_id}** - Modifier un profil médecin

```json
{
  "license_number": "FR-NEU-2024-001-UPD",
  "specialty": "Neurology",
  "sub_specialties": ["Neurosurgery", "Oncology"],
  "years_of_experience": 16,
  "education": [
    {
      "degree": "Doctorat en Médecine",
      "institution": "Université Paris Descartes",
      "graduation_year": "2009",
      "country": "France"
    },
    {
      "degree": "Spécialisation en Neurologie",
      "institution": "Hôpital Pitié-Salpêtrière",
      "graduation_year": "2014",
      "country": "France"
    },
    {
      "degree": "Formation en Neuro-oncologie",
      "institution": "Institut Gustave Roussy",
      "graduation_year": "2020",
      "country": "France"
    }
  ],
  "certifications": [
    {
      "name": "Certification Européenne de Neurologie",
      "issuing_body": "European Board of Neurology",
      "issue_date": "2014-06-15",
      "expiry_date": "2024-06-15",
      "certificate_number": "EBN-2014-5678",
      "is_active": true
    },
    {
      "name": "Certification en Neuro-oncologie",
      "issuing_body": "Société Française de Neuro-oncologie",
      "issue_date": "2020-09-10",
      "expiry_date": "2025-09-10",
      "certificate_number": "SFNO-2020-1234",
      "is_active": true
    }
  ],
  "languages_spoken": ["Français", "Anglais", "Espagnol", "Italien"],
  "consultation_fee": "200€",
  "schedule": [
    {
      "day_of_week": "Lundi",
      "start_time": "08:30",
      "end_time": "17:30",
      "is_available": true,
      "notes": "Consultations générales et spécialisées"
    },
    {
      "day_of_week": "Mardi",
      "start_time": "09:00",
      "end_time": "17:00",
      "is_available": true,
      "notes": "Consultations neuro-oncologie"
    },
    {
      "day_of_week": "Mercredi",
      "start_time": "08:00",
      "end_time": "16:00",
      "is_available": true,
      "notes": "Chirurgies programmées"
    },
    {
      "day_of_week": "Jeudi",
      "start_time": "09:00",
      "end_time": "17:00",
      "is_available": true,
      "notes": "Consultations et suivis"
    },
    {
      "day_of_week": "Vendredi",
      "start_time": "09:00",
      "end_time": "15:00",
      "is_available": true,
      "notes": "Recherche et formation"
    }
  ],
  "status": "Active",
  "bio": "Dr. Jean Dupont est un neurologue et neuro-oncologue expérimenté avec 16 ans d'expérience. Il se spécialise dans le traitement des tumeurs cérébrales complexes et est reconnu internationalement pour ses innovations en neurochirurgie. Il parle couramment quatre langues et accueille des patients du monde entier."
}
```

### **DELETE /doctors/{doctor_id}** - Supprimer un profil médecin
*Pas de body - Remplacer {doctor_id} par un ID réel*

### **GET /doctors/by-specialty/{specialty}** - Médecins par spécialité
*Pas de body - Remplacer {specialty} par :*
- `Neurology`
- `Oncology`
- `Radiology`
- `Neurosurgery`
- `General Medicine`
- `Psychiatry`
- `Anesthesiology`

### **GET /doctors/{doctor_id}/schedule** - Emploi du temps d'un médecin
*Pas de body - Remplacer {doctor_id} par un ID réel*

### **GET /doctors/statistics** - Statistiques des médecins
*Pas de body - Nécessite un token d'authentification avec permissions*

---

## 📊 **4. ENDPOINTS DE STATISTIQUES**

### **GET /health** - Vérification de l'état de l'API
*Pas de body*

### **GET /** - Endpoint racine
*Pas de body*

---

## 🔧 **5. EXEMPLES DE TESTS COMPLETS**

### **Scénario 1 : Créer un nouveau médecin complet**

1. **Se connecter en tant qu'admin :**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

2. **Créer un utilisateur médecin :**
```json
{
  "first_name": "Marie",
  "last_name": "Curie",
  "email": "marie.curie@test.com",
  "phone": "+33123456799",
  "gender": "Female",
  "date_of_birth": "1980-11-07",
  "address": "789 Boulevard Science, 75005 Paris",
  "role": "Doctor",
  "status": "Active",
  "is_verified": true,
  "profile_picture": null,
  "notes": "Radiologue spécialisée",
  "username": "dr.curie",
  "password": "curie123",
  "confirm_password": "curie123"
}
```

3. **Créer le profil médecin (utiliser l'ID retourné) :**
```json
{
  "user_id": "ID_UTILISATEUR_RETOURNE",
  "license_number": "FR-RAD-2024-002",
  "specialty": "Radiology",
  "sub_specialties": [],
  "years_of_experience": 12,
  "education": [
    {
      "degree": "Doctorat en Médecine",
      "institution": "Université Pierre et Marie Curie",
      "graduation_year": "2012",
      "country": "France"
    }
  ],
  "certifications": [
    {
      "name": "Certification en Radiologie",
      "issuing_body": "Société Française de Radiologie",
      "issue_date": "2015-03-20",
      "expiry_date": "2025-03-20",
      "certificate_number": "SFR-2015-9876",
      "is_active": true
    }
  ],
  "languages_spoken": ["Français", "Anglais"],
  "consultation_fee": "120€",
  "schedule": [
    {
      "day_of_week": "Lundi",
      "start_time": "08:00",
      "end_time": "16:00",
      "is_available": true,
      "notes": "Examens radiologiques"
    }
  ],
  "status": "Active",
  "bio": "Dr. Marie Curie est une radiologue expérimentée spécialisée dans l'imagerie médicale avancée.",
  "rating": 4.9,
  "total_reviews": 156
}
```

### **Scénario 2 : Rechercher des médecins**

1. **Tous les neurologues :**
   - GET `/doctors/by-specialty/Neurology`

2. **Recherche par nom :**
   - GET `/doctors?search=martin`

3. **Médecins disponibles seulement :**
   - GET `/doctors?available_only=true`

---

## 🎯 **Notes Importantes**

1. **Authentification** : Après login, copiez le `access_token` et utilisez-le dans l'en-tête `Authorization: Bearer TOKEN`

2. **IDs dynamiques** : Remplacez les `{user_id}` et `{doctor_id}` par les vrais IDs retournés par l'API

3. **Permissions** : Certaines actions nécessitent des rôles spécifiques (Admin pour gérer les utilisateurs)

4. **Validation** : L'API valide automatiquement tous les champs selon les règles définies

5. **Erreurs courantes** :
   - Email déjà utilisé
   - Nom d'utilisateur déjà pris
   - Numéro de licence déjà utilisé
   - Permissions insuffisantes
