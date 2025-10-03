# 🧪 Exemples de Tests Swagger - Scripts de Body Complets

## 🚀 **Démarrage Rapide**

1. **Démarrer l'API :**
```bash
cd backend
python main_users_api.py
```

2. **Ouvrir Swagger :** http://localhost:8002/docs

3. **Comptes de test disponibles :**
- **Admin** : `admin` / `admin123`
- **Médecin 1** : `dr.martin` / `doctor123`
- **Médecin 2** : `dr.dubois` / `onco123`
- **Infirmière** : `nurse.claire` / `nurse123`

---

## 🔐 **AUTHENTIFICATION - Scripts de Body**

### **1. POST /auth/login** - Se connecter

**Admin :**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Médecin :**
```json
{
  "username": "dr.martin",
  "password": "doctor123"
}
```

**Infirmière :**
```json
{
  "username": "nurse.claire",
  "password": "nurse123"
}
```

### **2. POST /auth/register** - Créer un nouvel utilisateur

**Nouveau médecin :**
```json
{
  "first_name": "Alexandre",
  "last_name": "Dumas",
  "email": "alexandre.dumas@test.com",
  "phone": "+33123456788",
  "gender": "Male",
  "date_of_birth": "1982-07-24",
  "address": "123 Rue Littéraire, 75007 Paris",
  "role": "Doctor",
  "status": "Active",
  "is_verified": true,
  "profile_picture": null,
  "notes": "Psychiatre spécialisé",
  "username": "dr.dumas",
  "password": "dumas123",
  "confirm_password": "dumas123"
}
```

**Nouvelle infirmière :**
```json
{
  "first_name": "Amélie",
  "last_name": "Poulain",
  "email": "amelie.poulain@test.com",
  "phone": "+33123456787",
  "gender": "Female",
  "date_of_birth": "1995-04-15",
  "address": "456 Rue Montmartre, 75018 Paris",
  "role": "Nurse",
  "status": "Active",
  "is_verified": true,
  "profile_picture": null,
  "notes": "Infirmière en pédiatrie",
  "username": "nurse.amelie",
  "password": "amelie123",
  "confirm_password": "amelie123"
}
```

**Nouveau technicien :**
```json
{
  "first_name": "Thomas",
  "last_name": "Edison",
  "email": "thomas.edison@test.com",
  "phone": "+33123456786",
  "gender": "Male",
  "date_of_birth": "1987-02-11",
  "address": "789 Avenue Innovation, 75011 Paris",
  "role": "Technician",
  "status": "Active",
  "is_verified": true,
  "profile_picture": null,
  "notes": "Technicien en imagerie IRM",
  "username": "tech.edison",
  "password": "edison123",
  "confirm_password": "edison123"
}
```

**Nouvelle réceptionniste :**
```json
{
  "first_name": "Coco",
  "last_name": "Chanel",
  "email": "coco.chanel@test.com",
  "phone": "+33123456785",
  "gender": "Female",
  "date_of_birth": "1990-08-19",
  "address": "321 Rue Élégance, 75001 Paris",
  "role": "Receptionist",
  "status": "Active",
  "is_verified": true,
  "profile_picture": null,
  "notes": "Réceptionniste VIP",
  "username": "reception.coco",
  "password": "coco123",
  "confirm_password": "coco123"
}
```

---

## 👥 **GESTION UTILISATEURS - Scripts de Body**

### **3. PUT /users/{user_id}** - Modifier un utilisateur

**Mise à jour profil utilisateur :**
```json
{
  "first_name": "Alexandre-Marie",
  "last_name": "Dumas-Fils",
  "email": "alexandre.dumas.updated@test.com",
  "phone": "+33123456799",
  "gender": "Male",
  "date_of_birth": "1982-07-24",
  "address": "456 Boulevard Littéraire, 75008 Paris",
  "role": "Doctor",
  "status": "Active",
  "department": "Psychiatrie",
  "employee_id": "PSY001",
  "profile_picture": "https://example.com/photos/dumas.jpg",
  "notes": "Psychiatre spécialisé en neuropsychiatrie - Profil mis à jour"
}
```

---

## 🩺 **GESTION MÉDECINS - Scripts de Body**

### **4. POST /doctors** - Créer un profil médecin

**Profil médecin psychiatre :**
```json
{
  "user_id": "REMPLACER_PAR_ID_UTILISATEUR",
  "license_number": "FR-PSY-2024-003",
  "specialty": "Psychiatry",
  "sub_specialties": [],
  "years_of_experience": 8,
  "education": [
    {
      "degree": "Doctorat en Médecine",
      "institution": "Université Paris Diderot",
      "graduation_year": "2016",
      "country": "France"
    },
    {
      "degree": "Spécialisation en Psychiatrie",
      "institution": "Hôpital Sainte-Anne",
      "graduation_year": "2020",
      "country": "France"
    }
  ],
  "certifications": [
    {
      "name": "Certification en Psychiatrie Générale",
      "issuing_body": "Collège National des Psychiatres",
      "issue_date": "2020-07-15",
      "expiry_date": "2030-07-15",
      "certificate_number": "CNP-2020-3456",
      "is_active": true
    }
  ],
  "languages_spoken": ["Français", "Anglais", "Allemand"],
  "consultation_fee": "100€",
  "schedule": [
    {
      "day_of_week": "Lundi",
      "start_time": "10:00",
      "end_time": "18:00",
      "is_available": true,
      "notes": "Consultations individuelles"
    },
    {
      "day_of_week": "Mardi",
      "start_time": "09:00",
      "end_time": "17:00",
      "is_available": true,
      "notes": "Thérapies de groupe"
    },
    {
      "day_of_week": "Mercredi",
      "start_time": "14:00",
      "end_time": "20:00",
      "is_available": true,
      "notes": "Consultations urgentes"
    },
    {
      "day_of_week": "Jeudi",
      "start_time": "10:00",
      "end_time": "18:00",
      "is_available": true,
      "notes": "Suivis thérapeutiques"
    },
    {
      "day_of_week": "Vendredi",
      "start_time": "09:00",
      "end_time": "16:00",
      "is_available": true,
      "notes": "Consultations et recherche"
    }
  ],
  "status": "Active",
  "bio": "Dr. Alexandre Dumas est un psychiatre expérimenté spécialisé dans les troubles de l'humeur et les thérapies cognitivo-comportementales. Il a 8 ans d'expérience et est reconnu pour son approche empathique et ses méthodes innovantes.",
  "rating": 4.6,
  "total_reviews": 73
}
```

**Profil médecin anesthésiste :**
```json
{
  "user_id": "REMPLACER_PAR_ID_UTILISATEUR",
  "license_number": "FR-ANE-2024-004",
  "specialty": "Anesthesiology",
  "sub_specialties": [],
  "years_of_experience": 15,
  "education": [
    {
      "degree": "Doctorat en Médecine",
      "institution": "Université Claude Bernard Lyon 1",
      "graduation_year": "2009",
      "country": "France"
    },
    {
      "degree": "Spécialisation en Anesthésie-Réanimation",
      "institution": "CHU de Lyon",
      "graduation_year": "2014",
      "country": "France"
    }
  ],
  "certifications": [
    {
      "name": "Diplôme d'Anesthésie-Réanimation",
      "issuing_body": "Collège Français d'Anesthésie-Réanimation",
      "issue_date": "2014-11-20",
      "expiry_date": "2024-11-20",
      "certificate_number": "CFAR-2014-7890",
      "is_active": true
    },
    {
      "name": "Formation en Anesthésie Pédiatrique",
      "issuing_body": "Société Française d'Anesthésie Pédiatrique",
      "issue_date": "2018-05-10",
      "expiry_date": "2028-05-10",
      "certificate_number": "SFAP-2018-1122",
      "is_active": true
    }
  ],
  "languages_spoken": ["Français", "Anglais", "Espagnol"],
  "consultation_fee": "150€",
  "schedule": [
    {
      "day_of_week": "Lundi",
      "start_time": "07:00",
      "end_time": "19:00",
      "is_available": true,
      "notes": "Bloc opératoire - Chirurgies programmées"
    },
    {
      "day_of_week": "Mardi",
      "start_time": "07:00",
      "end_time": "19:00",
      "is_available": true,
      "notes": "Bloc opératoire - Neurochirurgie"
    },
    {
      "day_of_week": "Mercredi",
      "start_time": "08:00",
      "end_time": "16:00",
      "is_available": true,
      "notes": "Consultations pré-opératoires"
    },
    {
      "day_of_week": "Jeudi",
      "start_time": "07:00",
      "end_time": "19:00",
      "is_available": true,
      "notes": "Bloc opératoire - Urgences"
    },
    {
      "day_of_week": "Vendredi",
      "start_time": "08:00",
      "end_time": "17:00",
      "is_available": true,
      "notes": "Formation et recherche"
    }
  ],
  "status": "Active",
  "bio": "Dr. spécialisé en anesthésie-réanimation avec 15 ans d'expérience. Expert en anesthésie pour neurochirurgie et chirurgie pédiatrique. Reconnu pour sa précision technique et sa gestion des cas complexes.",
  "rating": 4.8,
  "total_reviews": 142
}
```

### **5. PUT /doctors/{doctor_id}** - Modifier un profil médecin

**Mise à jour profil médecin :**
```json
{
  "license_number": "FR-PSY-2024-003-UPD",
  "specialty": "Psychiatry",
  "sub_specialties": ["General Medicine"],
  "years_of_experience": 9,
  "education": [
    {
      "degree": "Doctorat en Médecine",
      "institution": "Université Paris Diderot",
      "graduation_year": "2016",
      "country": "France"
    },
    {
      "degree": "Spécialisation en Psychiatrie",
      "institution": "Hôpital Sainte-Anne",
      "graduation_year": "2020",
      "country": "France"
    },
    {
      "degree": "Formation en Neuropsychiatrie",
      "institution": "Institut du Cerveau",
      "graduation_year": "2023",
      "country": "France"
    }
  ],
  "certifications": [
    {
      "name": "Certification en Psychiatrie Générale",
      "issuing_body": "Collège National des Psychiatres",
      "issue_date": "2020-07-15",
      "expiry_date": "2030-07-15",
      "certificate_number": "CNP-2020-3456",
      "is_active": true
    },
    {
      "name": "Certification en Neuropsychiatrie",
      "issuing_body": "Société Française de Neuropsychiatrie",
      "issue_date": "2023-09-20",
      "expiry_date": "2033-09-20",
      "certificate_number": "SFNP-2023-5678",
      "is_active": true
    }
  ],
  "languages_spoken": ["Français", "Anglais", "Allemand", "Italien"],
  "consultation_fee": "120€",
  "schedule": [
    {
      "day_of_week": "Lundi",
      "start_time": "09:00",
      "end_time": "18:00",
      "is_available": true,
      "notes": "Consultations individuelles et neuropsychiatrie"
    },
    {
      "day_of_week": "Mardi",
      "start_time": "09:00",
      "end_time": "17:00",
      "is_available": true,
      "notes": "Thérapies de groupe et formations"
    },
    {
      "day_of_week": "Mercredi",
      "start_time": "13:00",
      "end_time": "20:00",
      "is_available": true,
      "notes": "Consultations urgentes et suivis"
    },
    {
      "day_of_week": "Jeudi",
      "start_time": "10:00",
      "end_time": "18:00",
      "is_available": true,
      "notes": "Recherche et consultations spécialisées"
    },
    {
      "day_of_week": "Vendredi",
      "start_time": "09:00",
      "end_time": "16:00",
      "is_available": true,
      "notes": "Consultations et supervision"
    }
  ],
  "status": "Active",
  "bio": "Dr. Alexandre Dumas est un psychiatre et neuropsychiatre expérimenté avec 9 ans d'expérience. Spécialisé dans les troubles de l'humeur, les thérapies cognitivo-comportementales et la neuropsychiatrie. Il a récemment complété une formation avancée en neuropsychiatrie et est reconnu pour son approche innovante combinant psychiatrie traditionnelle et neurosciences modernes."
}
```

---

## 🧪 **SCÉNARIOS DE TESTS COMPLETS**

### **Scénario 1 : Workflow Complet - Créer un Médecin Généraliste**

**Étape 1 - Se connecter en admin :**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Étape 2 - Créer l'utilisateur :**
```json
{
  "first_name": "Victor",
  "last_name": "Hugo",
  "email": "victor.hugo@test.com",
  "phone": "+33123456784",
  "gender": "Male",
  "date_of_birth": "1975-02-26",
  "address": "123 Place des Vosges, 75004 Paris",
  "role": "Doctor",
  "status": "Active",
  "is_verified": true,
  "profile_picture": null,
  "notes": "Médecin généraliste expérimenté",
  "username": "dr.hugo",
  "password": "hugo123",
  "confirm_password": "hugo123"
}
```

**Étape 3 - Créer le profil médecin (remplacer user_id) :**
```json
{
  "user_id": "COPIER_ID_DE_ETAPE_2",
  "license_number": "FR-GEN-2024-005",
  "specialty": "General Medicine",
  "sub_specialties": [],
  "years_of_experience": 25,
  "education": [
    {
      "degree": "Doctorat en Médecine",
      "institution": "Université Paris Descartes",
      "graduation_year": "1999",
      "country": "France"
    }
  ],
  "certifications": [
    {
      "name": "Diplôme de Médecine Générale",
      "issuing_body": "Conseil National de l'Ordre des Médecins",
      "issue_date": "1999-12-15",
      "expiry_date": "2029-12-15",
      "certificate_number": "CNOM-1999-9999",
      "is_active": true
    }
  ],
  "languages_spoken": ["Français", "Anglais"],
  "consultation_fee": "60€",
  "schedule": [
    {
      "day_of_week": "Lundi",
      "start_time": "08:00",
      "end_time": "19:00",
      "is_available": true,
      "notes": "Consultations générales"
    },
    {
      "day_of_week": "Mardi",
      "start_time": "08:00",
      "end_time": "19:00",
      "is_available": true,
      "notes": "Consultations et visites à domicile"
    },
    {
      "day_of_week": "Mercredi",
      "start_time": "08:00",
      "end_time": "12:00",
      "is_available": true,
      "notes": "Consultations matinales"
    },
    {
      "day_of_week": "Jeudi",
      "start_time": "08:00",
      "end_time": "19:00",
      "is_available": true,
      "notes": "Consultations et urgences"
    },
    {
      "day_of_week": "Vendredi",
      "start_time": "08:00",
      "end_time": "18:00",
      "is_available": true,
      "notes": "Consultations et formation continue"
    },
    {
      "day_of_week": "Samedi",
      "start_time": "09:00",
      "end_time": "13:00",
      "is_available": true,
      "notes": "Consultations week-end"
    }
  ],
  "status": "Active",
  "bio": "Dr. Victor Hugo est un médecin généraliste avec 25 ans d'expérience. Il offre des soins complets pour toute la famille, des consultations préventives aux urgences. Reconnu pour son écoute attentive et son approche humaine de la médecine.",
  "rating": 4.9,
  "total_reviews": 287
}
```

### **Scénario 2 : Créer une Équipe Médicale Complète**

**Radiologue :**
```json
{
  "first_name": "Marie",
  "last_name": "Curie",
  "email": "marie.curie@test.com",
  "phone": "+33123456783",
  "gender": "Female",
  "date_of_birth": "1978-11-07",
  "address": "456 Rue de la Science, 75005 Paris",
  "role": "Doctor",
  "status": "Active",
  "is_verified": true,
  "profile_picture": null,
  "notes": "Radiologue spécialisée en imagerie cérébrale",
  "username": "dr.curie",
  "password": "curie123",
  "confirm_password": "curie123"
}
```

**Profil médecin radiologue :**
```json
{
  "user_id": "COPIER_ID_UTILISATEUR_CURIE",
  "license_number": "FR-RAD-2024-006",
  "specialty": "Radiology",
  "sub_specialties": ["Neurology"],
  "years_of_experience": 18,
  "education": [
    {
      "degree": "Doctorat en Médecine",
      "institution": "Université Pierre et Marie Curie",
      "graduation_year": "2006",
      "country": "France"
    },
    {
      "degree": "Spécialisation en Radiologie",
      "institution": "Hôpital Pitié-Salpêtrière",
      "graduation_year": "2011",
      "country": "France"
    }
  ],
  "certifications": [
    {
      "name": "Diplôme de Radiologie et Imagerie Médicale",
      "issuing_body": "Société Française de Radiologie",
      "issue_date": "2011-06-30",
      "expiry_date": "2031-06-30",
      "certificate_number": "SFR-2011-1234",
      "is_active": true
    }
  ],
  "languages_spoken": ["Français", "Anglais", "Polonais"],
  "consultation_fee": "130€",
  "schedule": [
    {
      "day_of_week": "Lundi",
      "start_time": "07:30",
      "end_time": "17:30",
      "is_available": true,
      "notes": "IRM et Scanner cérébral"
    },
    {
      "day_of_week": "Mardi",
      "start_time": "07:30",
      "end_time": "17:30",
      "is_available": true,
      "notes": "Examens d'urgence"
    },
    {
      "day_of_week": "Mercredi",
      "start_time": "08:00",
      "end_time": "16:00",
      "is_available": true,
      "notes": "Consultations et interprétations"
    },
    {
      "day_of_week": "Jeudi",
      "start_time": "07:30",
      "end_time": "17:30",
      "is_available": true,
      "notes": "Examens programmés"
    },
    {
      "day_of_week": "Vendredi",
      "start_time": "08:00",
      "end_time": "15:00",
      "is_available": true,
      "notes": "Recherche et formation"
    }
  ],
  "status": "Active",
  "bio": "Dr. Marie Curie est une radiologue experte en imagerie cérébrale avec 18 ans d'expérience. Spécialisée dans le diagnostic des tumeurs cérébrales et des pathologies neurologiques. Pionnière dans l'utilisation de l'IA pour l'analyse d'images médicales.",
  "rating": 4.9,
  "total_reviews": 156
}
```

---

## 🔍 **TESTS DE RECHERCHE ET FILTRAGE**

### **Recherche de médecins par spécialité :**
- **GET** `/doctors/by-specialty/Neurology`
- **GET** `/doctors/by-specialty/Oncology`
- **GET** `/doctors/by-specialty/Radiology`
- **GET** `/doctors/by-specialty/Psychiatry`
- **GET** `/doctors/by-specialty/General Medicine`

### **Recherche d'utilisateurs :**
- **GET** `/users?search=martin`
- **GET** `/users?role=Doctor`
- **GET** `/users?status=Active`
- **GET** `/users?role=Doctor&status=Active&search=sarah`

### **Filtrage des médecins :**
- **GET** `/doctors?specialty=Neurology`
- **GET** `/doctors?available_only=true`
- **GET** `/doctors?search=martin&specialty=Neurology`
- **GET** `/doctors?status=Active&specialty=Oncology`

---

## ⚠️ **TESTS D'ERREURS ET VALIDATION**

### **Test 1 : Mots de passe non correspondants**
```json
{
  "first_name": "Test",
  "last_name": "Erreur",
  "email": "test.erreur@test.com",
  "phone": "+33123456700",
  "gender": "Male",
  "date_of_birth": "1985-01-01",
  "address": "123 Rue Test",
  "role": "Doctor",
  "status": "Active",
  "is_verified": true,
  "username": "test.erreur",
  "password": "motdepasse123",
  "confirm_password": "motdepasse456"
}
```
**Résultat attendu :** Erreur 400 - "Les mots de passe ne correspondent pas"

### **Test 2 : Email déjà existant**
```json
{
  "first_name": "Test",
  "last_name": "Doublon",
  "email": "admin@cerebloom.com",
  "phone": "+33123456701",
  "gender": "Male",
  "date_of_birth": "1985-01-01",
  "address": "123 Rue Test",
  "role": "Doctor",
  "status": "Active",
  "is_verified": true,
  "username": "test.doublon",
  "password": "motdepasse123",
  "confirm_password": "motdepasse123"
}
```
**Résultat attendu :** Erreur 400 - "Un utilisateur avec cet email existe déjà"

### **Test 3 : Nom d'utilisateur déjà pris**
```json
{
  "first_name": "Test",
  "last_name": "Username",
  "email": "test.username@test.com",
  "phone": "+33123456702",
  "gender": "Male",
  "date_of_birth": "1985-01-01",
  "address": "123 Rue Test",
  "role": "Doctor",
  "status": "Active",
  "is_verified": true,
  "username": "admin",
  "password": "motdepasse123",
  "confirm_password": "motdepasse123"
}
```
**Résultat attendu :** Erreur 400 - "Ce nom d'utilisateur est déjà pris"

### **Test 4 : Numéro de licence déjà utilisé**
```json
{
  "user_id": "USER_ID_VALIDE",
  "license_number": "FR-NEU-2005-001",
  "specialty": "Neurology",
  "sub_specialties": [],
  "years_of_experience": 10,
  "education": [],
  "certifications": [],
  "languages_spoken": ["Français"],
  "consultation_fee": "100€",
  "schedule": [],
  "status": "Active",
  "bio": "Test",
  "rating": 0,
  "total_reviews": 0
}
```
**Résultat attendu :** Erreur 400 - "Ce numéro de licence est déjà utilisé"

### **Test 5 : Connexion avec mauvais mot de passe**
```json
{
  "username": "admin",
  "password": "mauvais_mot_de_passe"
}
```
**Résultat attendu :** Erreur 401 - "Nom d'utilisateur ou mot de passe incorrect"

---

## 📋 **GUIDE D'UTILISATION SWAGGER**

### **🔑 Étapes d'authentification :**

1. **Se connecter :**
   - Utiliser **POST** `/auth/login`
   - Copier le `access_token` de la réponse

2. **Autoriser dans Swagger :**
   - Cliquer sur le bouton **"Authorize"** en haut à droite
   - Entrer : `Bearer VOTRE_ACCESS_TOKEN`
   - Cliquer **"Authorize"**

3. **Tester les endpoints protégés :**
   - Maintenant vous pouvez accéder aux endpoints nécessitant une authentification

### **📝 Remplacement des IDs :**

- **{user_id}** : Remplacer par un ID d'utilisateur réel (ex: `123e4567-e89b-12d3-a456-426614174000`)
- **{doctor_id}** : Remplacer par un ID de médecin réel
- **USER_ID_ICI** : Copier l'ID retourné lors de la création d'un utilisateur

### **🎯 Endpoints à tester en priorité :**

1. **GET** `/health` - Vérifier que l'API fonctionne
2. **POST** `/auth/login` - Se connecter avec un compte existant
3. **GET** `/auth/me` - Voir son profil
4. **GET** `/doctors` - Liste publique des médecins
5. **GET** `/users` - Liste des utilisateurs (Admin seulement)
6. **POST** `/auth/register` - Créer un nouvel utilisateur
7. **POST** `/doctors` - Créer un profil médecin

### **⚡ Raccourcis de test :**

**Test rapide complet :**
1. Login admin → GET `/users` → POST `/auth/register` → POST `/doctors`
2. Login médecin → GET `/auth/me` → PUT `/doctors/{id}`
3. Public → GET `/doctors` → GET `/doctors/by-specialty/Neurology`

---

## 🎯 **CODES DE RÉPONSE HTTP**

- **200** ✅ : Succès (GET, PUT)
- **201** ✅ : Créé avec succès (POST)
- **204** ✅ : Supprimé avec succès (DELETE)
- **400** ❌ : Erreur de validation (données incorrectes)
- **401** ❌ : Non authentifié (token manquant/invalide)
- **403** ❌ : Permissions insuffisantes
- **404** ❌ : Ressource non trouvée
- **423** ❌ : Compte verrouillé (trop de tentatives)

---

## 🚀 **CONSEILS POUR LES TESTS**

### **✅ Bonnes pratiques :**
- Toujours tester `/health` en premier
- Se connecter avant de tester les endpoints protégés
- Copier les IDs retournés pour les utiliser dans d'autres tests
- Tester les cas d'erreur pour valider la robustesse

### **🔄 Ordre de test recommandé :**
1. **Santé** : GET `/health`
2. **Authentification** : POST `/auth/login`
3. **Profil** : GET `/auth/me`
4. **Lecture** : GET `/users`, GET `/doctors`
5. **Création** : POST `/auth/register`, POST `/doctors`
6. **Modification** : PUT `/users/{id}`, PUT `/doctors/{id}`
7. **Recherche** : GET avec paramètres de filtrage
8. **Erreurs** : Tests de validation

### **🎯 Points d'attention :**
- Les tokens expirent après 30 minutes
- Certains endpoints nécessitent des rôles spécifiques
- Les IDs sont générés automatiquement (UUID)
- La validation est stricte sur les formats (email, téléphone, dates)

Bon test ! 🧪✨
