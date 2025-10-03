# 🧠 CereBloom - Architecture Base de Données Complète

## 📋 Vue d'Ensemble de l'Architecture

CereBloom est une application de cabinet médical spécialisée dans la **segmentation de tumeurs cérébrales** avec IA intégrée.

### 🎯 **Patterns de Conception Utilisés :**

1. **🔐 Pattern Authentification/Autorisation**
2. **👥 Pattern Gestion des Rôles (RBAC)**
3. **🩺 Pattern Profil Spécialisé (Médecins)**
4. **🧠 Pattern IA Segmentation (Cœur Métier)**
5. **🔄 Pattern Session Management**
6. **📦 Pattern DTO (Data Transfer Object)**
7. **🧩 Pattern Composition**
8. **🔗 Pattern Relations (One-to-One, One-to-Many)**

---

## 🗄️ **TABLEAUX DE BASE DE DONNÉES COMPLETS**

#### **Table: users**
| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Identifiant unique UUID |
| first_name | VARCHAR(100) | NOT NULL | Prénom |
| last_name | VARCHAR(100) | NOT NULL | Nom de famille |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email unique |
| phone | VARCHAR(20) | | Téléphone |
| role | ENUM('ADMIN', 'DOCTOR', 'SECRETARY') | NOT NULL | Rôle utilisateur |
| status | ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED', 'PENDING_VERIFICATION') | DEFAULT 'PENDING_VERIFICATION' | Statut du compte |
| is_verified | BOOLEAN | DEFAULT FALSE | Email vérifié |
| profile_picture | VARCHAR(500) | | URL photo de profil |
| department | VARCHAR(100) | | Département |
| employee_id | VARCHAR(50) | | ID employé |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date de création |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Dernière modification |
| created_by | VARCHAR(36) | FOREIGN KEY | Créé par (user_id) |
| last_activity | TIMESTAMP | | Dernière activité |

#### **Table: user_credentials**
| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Identifiant unique |
| user_id | VARCHAR(36) | FOREIGN KEY, UNIQUE | Référence vers users.id |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Nom d'utilisateur |
| password_hash | VARCHAR(255) | NOT NULL | Mot de passe haché |
| salt | VARCHAR(255) | NOT NULL | Salt pour hachage |
| last_login | TIMESTAMP | | Dernière connexion |
| failed_login_attempts | INT | DEFAULT 0 | Tentatives échouées |
| is_locked | BOOLEAN | DEFAULT FALSE | Compte verrouillé |
| locked_until | TIMESTAMP | | Fin du verrouillage |
| reset_token | VARCHAR(255) | | Token de réinitialisation |
| token_expires_at | TIMESTAMP | | Expiration du token |

#### **Table: user_permissions**
| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | VARCHAR(36) | PRIMARY KEY | Identifiant unique |
| user_id | VARCHAR(36) | FOREIGN KEY, UNIQUE | Référence vers users.id |
| can_view_patients | BOOLEAN | DEFAULT FALSE | Voir les patients |
| can_create_patients | BOOLEAN | DEFAULT FALSE | Créer des patients |
| can_edit_patients | BOOLEAN | DEFAULT FALSE | Modifier les patients |
| can_delete_patients | BOOLEAN | DEFAULT FALSE | Supprimer les patients |
| can_view_segmentations | BOOLEAN | DEFAULT FALSE | Voir les segmentations |
| can_create_segmentations | BOOLEAN | DEFAULT FALSE | Créer des segmentations |
| can_validate_segmentations | BOOLEAN | DEFAULT FALSE | Valider les segmentations |
| can_manage_appointments | BOOLEAN | DEFAULT FALSE | Gérer les rendez-vous |
| can_manage_users | BOOLEAN | DEFAULT FALSE | Gérer les utilisateurs |
| can_view_reports | BOOLEAN | DEFAULT FALSE | Voir les rapports |
| can_export_data | BOOLEAN | DEFAULT FALSE | Exporter les données |
| custom_permissions | JSON | | Permissions personnalisées |

#### **Table: user_sessions**
| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| session_id | VARCHAR(255) | PRIMARY KEY | Identifiant de session |
| user_id | VARCHAR(36) | FOREIGN KEY | Référence vers users.id |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Création de session |
| expires_at | TIMESTAMP | NOT NULL | Expiration |
| ip_address | VARCHAR(45) | | Adresse IP |
| user_agent | TEXT | | Navigateur |
| is_active | BOOLEAN | DEFAULT TRUE | Session active |
| last_activity | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Dernière activité |

### **👨‍⚕️ 2. SYSTÈME MÉDECINS**

---

### **2. Classes de Sécurité et Authentification**

#### **Credentials (Informations de Connexion) :**
```python
class UserCredentials(BaseModel):
    username: str                    # Nom d'utilisateur unique
    password_hash: str               # Mot de passe haché
    salt: str                        # Salt pour le hachage
    last_login: Optional[datetime]   # Dernière connexion
    failed_login_attempts: int       # Tentatives échouées
    is_locked: bool                  # Compte verrouillé
    locked_until: Optional[datetime] # Fin du verrouillage
    reset_token: Optional[str]       # Token de réinitialisation
```

#### **Permissions (Contrôle d'Accès) :**
```python
class UserPermissions(BaseModel):
    can_view_patients: bool          # Voir les patients
    can_create_patients: bool        # Créer des patients
    can_edit_patients: bool          # Modifier les patients
    can_delete_patients: bool        # Supprimer les patients
    can_view_scans: bool             # Voir les examens
    can_create_scans: bool           # Créer des examens
    # ... autres permissions
    can_manage_users: bool           # Gérer les utilisateurs
    custom_permissions: List[str]    # Permissions personnalisées
```

**Pattern RBAC (Role-Based Access Control) :**
- 🔐 **Permissions par rôle** : Chaque rôle a des permissions par défaut
- 🔐 **Permissions granulaires** : Contrôle fin des accès
- 🔐 **Permissions personnalisées** : Extensibilité

---

### **3. Classes Utilisateurs (Héritage)**

#### **Classe de Base :**
```python
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    gender: Gender
    date_of_birth: str
    address: str
    role: UserRole                   # Rôle dans le système
    status: UserStatus               # Statut du compte
    is_verified: bool                # Email vérifié
    profile_picture: Optional[str]   # Photo de profil
    notes: str
```

#### **Classe Complète :**
```python
class User(UserBase):
    id: str                          # Identifiant unique
    credentials: UserCredentials     # Informations de connexion
    permissions: UserPermissions     # Permissions d'accès
    department: Optional[str]        # Département
    employee_id: Optional[str]       # ID employé
    created_at: datetime             # Date de création
    updated_at: datetime             # Dernière modification
    last_activity: Optional[datetime] # Dernière activité
    created_by: str                  # Créé par (ID utilisateur)
```

**Pattern Composition :**
- 🧩 **User** contient **UserCredentials**
- 🧩 **User** contient **UserPermissions**
- 🧩 **Séparation des responsabilités** claires

---

### **4. Classes Médecins (Profil Spécialisé)**

#### **Données Éducation :**
```python
class DoctorEducation(BaseModel):
    degree: str                      # Diplôme
    institution: str                 # Institution
    graduation_year: str             # Année de diplôme
    country: str                     # Pays
```

#### **Certifications :**
```python
class DoctorCertification(BaseModel):
    name: str                        # Nom de la certification
    issuing_body: str                # Organisme émetteur
    issue_date: str                  # Date d'émission
    expiry_date: Optional[str]       # Date d'expiration
    certificate_number: str          # Numéro de certificat
    is_active: bool                  # Certification active
```

#### **Emploi du Temps :**
```python
class DoctorSchedule(BaseModel):
    day_of_week: str                 # Jour de la semaine
    start_time: str                  # Heure de début
    end_time: str                    # Heure de fin
    is_available: bool               # Disponible
    notes: Optional[str]             # Notes
```

#### **Profil Médecin Complet :**
```python
class Doctor(DoctorBase):
    id: str                          # ID unique du médecin
    user_id: str                     # Lien vers User
    license_number: str              # Numéro de licence
    specialty: DoctorSpecialty       # Spécialité principale
    sub_specialties: List[DoctorSpecialty] # Sous-spécialités
    years_of_experience: int         # Années d'expérience
    education: List[DoctorEducation] # Formation
    certifications: List[DoctorCertification] # Certifications
    languages_spoken: List[str]      # Langues parlées
    consultation_fee: str            # Tarif de consultation
    schedule: List[DoctorSchedule]   # Emploi du temps
    bio: Optional[str]               # Biographie
    rating: float                    # Note moyenne
    total_reviews: int               # Nombre d'avis
```

**Pattern Profil Spécialisé :**
- 🩺 **Extension du User** : Un médecin est un utilisateur avec des données supplémentaires
- 🩺 **Données métier** : Informations spécifiques au domaine médical
- 🩺 **Relation One-to-One** : Un utilisateur peut avoir un profil médecin

---

### **5. Classes de Session et Sécurité**

#### **Sessions Utilisateur :**
```python
class UserSession(BaseModel):
    session_id: str                  # ID de session
    user_id: str                     # ID utilisateur
    created_at: datetime             # Création
    expires_at: datetime             # Expiration
    ip_address: str                  # Adresse IP
    user_agent: str                  # Navigateur
    is_active: bool                  # Session active
    last_activity: Optional[datetime] # Dernière activité
```

#### **Tokens de Rafraîchissement :**
```python
class RefreshToken(BaseModel):
    token_id: str                    # ID du token
    user_id: str                     # ID utilisateur
    token_hash: str                  # Hash du token
    created_at: datetime             # Création
    expires_at: datetime             # Expiration
    is_revoked: bool                 # Token révoqué
    revoked_by: Optional[str]        # Révoqué par
    revoked_at: Optional[datetime]   # Date de révocation
```

**Pattern Session Management :**
- 🔄 **Sessions temporaires** : Tokens d'accès courts
- 🔄 **Refresh tokens** : Renouvellement sécurisé
- 🔄 **Révocation** : Invalidation des tokens
- 🔄 **Audit trail** : Traçabilité des connexions

---

### **6. Classes DTO (Data Transfer Object)**

#### **Pour l'Authentification :**
```python
class UserLogin(BaseModel):          # Connexion
    username: str
    password: str

class LoginResponse(BaseModel):      # Réponse de connexion
    access_token: str
    refresh_token: str
    user: UserResponse
    expires_at: datetime

class UserResponse(BaseModel):       # Réponse utilisateur
    user: User
    doctor_profile: Optional[Doctor]
    permissions: List[str]
    is_online: bool
```

#### **Pour les Opérations CRUD :**
```python
class UserCreate(UserBase):          # Création utilisateur
    username: str
    password: str
    confirm_password: str

class UserUpdate(BaseModel):         # Mise à jour (champs optionnels)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    # ... tous les champs optionnels

class DoctorPublicProfile(BaseModel): # Profil public médecin
    id: str
    first_name: str
    last_name: str
    specialty: DoctorSpecialty
    rating: float
    consultation_fee: str
    # ... informations publiques seulement
```

**Pattern DTO :**
- 📦 **Sécurité** : Contrôle des données exposées
- 📦 **Validation** : Règles spécifiques par opération
- 📦 **Documentation** : API claire et compréhensible

---

## 🔗 **Relations Entre Entités**

### **Relations Principales :**

```
User ||--o| Doctor : "peut être"
User ||--o{ UserSession : "a des sessions"
User ||--o{ RefreshToken : "a des tokens"
User ||--o{ Patient : "a créé" (via created_by)
Doctor ||--o{ Patient : "traite" (via assigned_doctor)
Doctor ||--o{ Scan : "effectue"
Doctor ||--o{ Treatment : "prescrit"
Doctor ||--o{ Appointment : "planifie"
```

### **Relations de Composition :**

```
User *-- UserCredentials : "contient"
User *-- UserPermissions : "contient"
Doctor *-- DoctorEducation : "contient"
Doctor *-- DoctorCertification : "contient"
Doctor *-- DoctorSchedule : "contient"
```

---

## 🎯 **Avantages de cette Architecture**

### **✅ Sécurité :**
- 🔐 **Authentification robuste** avec hachage sécurisé
- 🔐 **Gestion des sessions** avec expiration
- 🔐 **Contrôle d'accès granulaire** (RBAC)
- 🔐 **Protection contre les attaques** (brute force, etc.)

### **✅ Flexibilité :**
- 👥 **Rôles extensibles** : Facile d'ajouter de nouveaux rôles
- 🩺 **Profils spécialisés** : Médecins, futurs autres profils
- 📦 **Permissions personnalisées** : Adaptable aux besoins

### **✅ Maintenabilité :**
- 🧩 **Séparation des responsabilités** claire
- 📦 **DTOs spécialisés** pour chaque opération
- 🔗 **Relations bien définies** entre entités

### **✅ Évolutivité :**
- 🔄 **Ajout de nouveaux rôles** simplifié
- 🩺 **Nouveaux profils spécialisés** (infirmières, etc.)
- 📊 **Audit et statistiques** intégrés

Cette architecture offre une base solide pour un système de gestion hospitalière complet ! 🏥
