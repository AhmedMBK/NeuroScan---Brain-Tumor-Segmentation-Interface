# 🏗️ Architecture et Diagramme de Classes - API Patients

## 📋 Vue d'Ensemble

Notre API utilise une architecture en couches basée sur les **modèles Pydantic** et les **patterns de conception** suivants :

- **Pattern Repository** : Stockage en mémoire (extensible vers base de données)
- **Pattern DTO** : Classes séparées pour création/mise à jour/réponse
- **Pattern Composition** : Objets complexes composés d'objets plus simples
- **Pattern Énumération** : Types de données contrôlés et validés

## 🎯 Structure Hiérarchique

### 1. **Énumérations (Types Contrôlés)**

```python
# Exemples d'énumérations utilisées
class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female" 
    OTHER = "Other"

class BloodType(str, Enum):
    A_POSITIVE = "A+"
    O_NEGATIVE = "O-"
    # ... autres types
```

**Avantages :**
- ✅ **Validation automatique** des valeurs
- ✅ **Documentation intégrée** des valeurs possibles
- ✅ **Sécurité des types** en TypeScript (frontend)
- ✅ **Évite les erreurs** de saisie

### 2. **Classes de Données Imbriquées (Composition)**

```python
class EmergencyContact(BaseModel):
    name: str
    relationship: str
    phone: str

class Patient(BaseModel):
    # ... autres champs
    emergency_contact: EmergencyContact  # Composition
```

**Pattern Composition :**
- 🧩 **Réutilisabilité** : `EmergencyContact` peut être utilisé ailleurs
- 🧩 **Lisibilité** : Structure claire et organisée
- 🧩 **Validation** : Chaque composant est validé séparément
- 🧩 **Maintenance** : Modifications localisées

### 3. **Classes de Base (Héritage)**

```python
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    # ... tous les champs communs

class Patient(PatientBase):
    id: str                    # Ajouté pour l'entité persistée
    created_at: datetime       # Métadonnées
    updated_at: datetime

class PatientCreate(PatientBase):
    pass                       # Hérite de tous les champs de base

class PatientUpdate(BaseModel):
    first_name: Optional[str]  # Tous les champs optionnels
    last_name: Optional[str]
    # ... pour les mises à jour partielles
```

**Pattern Héritage :**
- 🔄 **DRY Principle** : Pas de duplication de code
- 🔄 **Cohérence** : Même structure pour toutes les opérations
- 🔄 **Évolutivité** : Facile d'ajouter de nouveaux champs

## 🔗 Relations entre Classes

### 1. **Relation 1-à-Plusieurs (One-to-Many)**

```python
# Un patient peut avoir plusieurs scans
Patient ||--o{ Scan

# Un patient peut avoir plusieurs traitements  
Patient ||--o{ Treatment

# Un patient peut avoir plusieurs rendez-vous
Patient ||--o{ Appointment
```

**Implémentation :**
```python
class Scan(BaseModel):
    patient_id: str  # Clé étrangère vers Patient

# Récupération des scans d'un patient
patient_scans = [s for s in scans_db.values() if s.patient_id == patient_id]
```

### 2. **Relation de Composition (Has-A)**

```python
# Un patient "a" un contact d'urgence
Patient *-- EmergencyContact

# Un patient "a" une assurance
Patient *-- Insurance

# Un scan "a" un résultat
Scan *-- ScanResult
```

**Implémentation :**
```python
class Patient(BaseModel):
    emergency_contact: EmergencyContact  # Objet imbriqué
    insurance: Insurance                 # Objet imbriqué
```

## 📊 Patterns de Conception Utilisés

### 1. **Pattern DTO (Data Transfer Object)**

```python
# Pour la création (sans ID, sans métadonnées)
class PatientCreate(PatientBase):
    pass

# Pour la mise à jour (tous champs optionnels)
class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    # ...

# Pour la réponse (avec métadonnées supplémentaires)
class PatientResponse(BaseModel):
    patient: Patient
    scans_count: int
    treatments_count: int
```

**Avantages :**
- 🎯 **Séparation des responsabilités**
- 🎯 **Validation spécifique** à chaque opération
- 🎯 **Sécurité** : Pas d'exposition de champs internes
- 🎯 **Documentation** : API claire pour les développeurs

### 2. **Pattern Repository (Stockage)**

```python
# Stockage en mémoire (simulant une base de données)
patients_db: Dict[str, Patient] = {}
scans_db: Dict[str, Scan] = {}
treatments_db: Dict[str, Treatment] = {}
appointments_db: Dict[str, Appointment] = {}

# Fonctions d'accès aux données
def get_patient_scans(patient_id: str) -> List[Scan]:
    return [s for s in scans_db.values() if s.patient_id == patient_id]
```

**Avantages :**
- 🗄️ **Abstraction** : Logique métier séparée du stockage
- 🗄️ **Testabilité** : Facile de mocker les données
- 🗄️ **Évolutivité** : Facile de passer à une vraie DB

### 3. **Pattern Validation (Pydantic)**

```python
class Patient(BaseModel):
    height: int = Field(..., gt=0, le=300, description="Taille en cm")
    weight: float = Field(..., gt=0, le=500, description="Poids en kg")
    email: EmailStr  # Validation automatique de l'email
    
    class Config:
        from_attributes = True  # Pour la sérialisation
```

**Avantages :**
- ✅ **Validation automatique** à l'entrée
- ✅ **Messages d'erreur** clairs
- ✅ **Documentation** auto-générée
- ✅ **Sérialisation** JSON automatique

## 🔄 Flux de Données

### 1. **Création d'un Patient**

```
Frontend → PatientCreate → Validation → Patient → patients_db
```

### 2. **Récupération avec Relations**

```
GET /patients/{id} → Patient + count(scans) + count(treatments) → PatientResponse
```

### 3. **Mise à Jour Partielle**

```
Frontend → PatientUpdate → Validation → Merge avec Patient existant → patients_db
```

## 🎨 Avantages de cette Architecture

### ✅ **Maintenabilité**
- Code organisé et modulaire
- Responsabilités bien séparées
- Facile à déboguer et tester

### ✅ **Évolutivité**
- Facile d'ajouter de nouveaux modèles
- Structure extensible pour nouvelles fonctionnalités
- Migration vers base de données simplifiée

### ✅ **Sécurité**
- Validation automatique des données
- Types contrôlés avec énumérations
- Pas d'exposition de données sensibles

### ✅ **Documentation**
- Auto-génération de la documentation Swagger
- Types explicites pour le frontend
- Exemples intégrés dans l'API

### ✅ **Performance**
- Validation rapide avec Pydantic
- Sérialisation optimisée
- Requêtes efficaces (même en mémoire)

## 🚀 Extensions Futures

### 1. **Base de Données**
```python
# Remplacement facile du stockage en mémoire
class PatientRepository:
    async def create(self, patient: PatientCreate) -> Patient:
        # Logique SQLAlchemy/MongoDB
```

### 2. **Cache**
```python
# Ajout de cache Redis
@lru_cache(maxsize=100)
def get_patient_summary(patient_id: str) -> PatientSummary:
```

### 3. **Authentification**
```python
# Ajout de sécurité
@app.get("/patients")
async def get_patients(current_user: User = Depends(get_current_user)):
```

Cette architecture offre une base solide et évolutive pour l'API de gestion des patients ! 🏗️
