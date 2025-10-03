#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API principale pour la gestion des patients - Point d'entrée principal.
"""

import uvicorn
from datetime import datetime

# Importer l'application et les modèles
from patients_api import (
    app, patients_db, scans_db, treatments_db, appointments_db,
    Patient, Scan, Treatment, Appointment,
    Gender, BloodType, ScanType, ScanStatus, TreatmentType, TreatmentStatus,
    Effectiveness, AppointmentStatus,
    EmergencyContact, Insurance, MedicalHistory, PastSurgery, ScanResult
)

# Importer tous les endpoints (cela enregistre automatiquement les routes)
try:
    import patients_endpoints
    import scans_endpoints
    import treatments_endpoints
    import appointments_endpoints
    print("✅ Tous les endpoints importés avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")

def create_sample_data():
    """Crée des données d'exemple pour tester l'API."""
    now = datetime.now()

    # Patients d'exemple
    sample_patients = [
        {
            "id": "patient-1",
            "first_name": "Jean",
            "last_name": "Dupont",
            "date_of_birth": "1980-05-15",
            "gender": Gender.MALE,
            "contact_number": "+33 1 23 45 67 89",
            "email": "jean.dupont@email.com",
            "address": "123 Rue de la Paix, 75001 Paris",
            "blood_type": BloodType.A_POSITIVE,
            "height": 180,
            "weight": 75.5,
            "emergency_contact": EmergencyContact(
                name="Marie Dupont",
                relationship="Épouse",
                phone="+33 1 23 45 67 90"
            ),
            "insurance": Insurance(
                provider="Sécurité Sociale",
                policy_number="1234567890123",
                expiry_date="2024-12-31"
            ),
            "doctor": "Dr. Sarah Martin",
            "medical_history": MedicalHistory(
                allergies=["Pénicilline"],
                chronic_conditions=["Hypertension"],
                past_surgeries=[
                    PastSurgery(
                        procedure="Appendicectomie",
                        date="2010-03-22",
                        notes="Aucune complication"
                    )
                ],
                family_history=["Diabète (Père)", "Cancer du sein (Mère)"]
            ),
            "notes": "Patient coopératif, suit bien les traitements.",
            "created_at": now,
            "updated_at": now
        },
        {
            "id": "patient-2",
            "first_name": "Marie",
            "last_name": "Martin",
            "date_of_birth": "1975-08-22",
            "gender": Gender.FEMALE,
            "contact_number": "+33 1 34 56 78 90",
            "email": "marie.martin@email.com",
            "address": "456 Avenue des Champs, 75008 Paris",
            "blood_type": BloodType.O_NEGATIVE,
            "height": 165,
            "weight": 62.0,
            "emergency_contact": EmergencyContact(
                name="Pierre Martin",
                relationship="Mari",
                phone="+33 1 34 56 78 91"
            ),
            "insurance": Insurance(
                provider="Mutuelle Générale",
                policy_number": "9876543210987",
                expiry_date="2024-06-30"
            ),
            "doctor": "Dr. Michel Dubois",
            "medical_history": MedicalHistory(
                allergies=["Sulfamides"],
                chronic_conditions=["Asthme", "Migraines"],
                past_surgeries=[
                    PastSurgery(
                        procedure="Césarienne",
                        date="2005-07-10",
                        notes="Naissance de jumeaux"
                    )
                ],
                family_history=["Maladie cardiaque (Père)", "AVC (Grand-père)"]
            ),
            "notes": "Patiente anxieuse, nécessite des explications détaillées.",
            "created_at": now,
            "updated_at": now
        }
    ]

    # Ajouter les patients à la base de données
    for patient_data in sample_patients:
        patient = Patient(**patient_data)
        patients_db[patient.id] = patient

    # Scans d'exemple
    sample_scans = [
        {
            "id": "scan-1",
            "patient_id": "patient-1",
            "date": "2023-10-12",
            "type": ScanType.MRI,
            "body_part": "Cerveau",
            "image_url": "https://example.com/scan1.jpg",
            "result": ScanResult(
                diagnosis="Glioblastome",
                tumor_type="Malin",
                tumor_size="3.2 cm",
                tumor_location="Lobe frontal droit",
                malignant=True,
                notes="Tumeur agressive avec œdème périphérique. Traitement immédiat recommandé."
            ),
            "doctor": "Dr. Sarah Martin",
            "facility": "Hôpital Saint-Louis",
            "status": ScanStatus.COMPLETED,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": "scan-2",
            "patient_id": "patient-2",
            "date": "2023-11-05",
            "type": ScanType.MRI,
            "body_part": "Cerveau",
            "image_url": "https://example.com/scan2.jpg",
            "result": ScanResult(
                diagnosis="Méningiome",
                tumor_type="Bénin",
                tumor_size="1.5 cm",
                tumor_location="Lobe temporal gauche",
                malignant=False,
                notes="Petite tumeur bénigne. Surveillance recommandée avec scan de contrôle dans 3 mois."
            ),
            "doctor": "Dr. Michel Dubois",
            "facility": "Hôpital Pitié-Salpêtrière",
            "status": ScanStatus.COMPLETED,
            "created_at": now,
            "updated_at": now
        }
    ]

    # Ajouter les scans à la base de données
    for scan_data in sample_scans:
        scan = Scan(**scan_data)
        scans_db[scan.id] = scan

    # Traitements d'exemple
    sample_treatments = [
        {
            "id": "treatment-1",
            "patient_id": "patient-1",
            "type": TreatmentType.MEDICATION,
            "name": "Témozolomide",
            "start_date": "2023-10-15",
            "end_date": None,
            "frequency": "Quotidien",
            "dosage": "150mg",
            "doctor": "Dr. Sarah Martin",
            "notes": "Médicament de chimiothérapie pour le traitement du glioblastome.",
            "status": TreatmentStatus.ACTIVE,
            "side_effects": ["Nausées", "Fatigue", "Diminution de l'appétit"],
            "effectiveness": Effectiveness.MODERATE,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": "treatment-2",
            "patient_id": "patient-2",
            "name": "Dexaméthasone",
            "type": TreatmentType.MEDICATION,
            "start_date": "2023-11-10",
            "end_date": None,
            "frequency": "Deux fois par jour",
            "dosage": "4mg",
            "doctor": "Dr. Michel Dubois",
            "notes": "Corticostéroïde pour réduire l'inflammation et la pression.",
            "status": TreatmentStatus.ACTIVE,
            "side_effects": ["Augmentation de l'appétit", "Changements d'humeur"],
            "effectiveness": Effectiveness.GOOD,
            "created_at": now,
            "updated_at": now
        }
    ]

    # Ajouter les traitements à la base de données
    for treatment_data in sample_treatments:
        treatment = Treatment(**treatment_data)
        treatments_db[treatment.id] = treatment

    # Rendez-vous d'exemple
    sample_appointments = [
        {
            "id": "appointment-1",
            "patient_id": "patient-1",
            "date": "2023-12-15",
            "time": "10:00",
            "doctor": "Dr. Sarah Martin",
            "purpose": "Suivi après radiothérapie",
            "notes": "Évaluer la réponse au traitement et gérer les effets secondaires.",
            "status": AppointmentStatus.SCHEDULED,
            "follow_up": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": "appointment-2",
            "patient_id": "patient-2",
            "date": "2024-01-10",
            "time": "14:30",
            "doctor": "Dr. Michel Dubois",
            "purpose": "Consultation de contrôle",
            "notes": "Vérifier l'évolution du méningiome et ajuster le traitement si nécessaire.",
            "status": AppointmentStatus.SCHEDULED,
            "follow_up": True,
            "created_at": now,
            "updated_at": now
        }
    ]

    # Ajouter les rendez-vous à la base de données
    for appointment_data in sample_appointments:
        appointment = Appointment(**appointment_data)
        appointments_db[appointment.id] = appointment

    # Mettre à jour les métadonnées des patients
    from patients_api import update_patient_metadata
    for patient_id in patients_db.keys():
        update_patient_metadata(patient_id)

    print("✅ Données d'exemple créées avec succès!")
    print(f"   - {len(patients_db)} patients")
    print(f"   - {len(scans_db)} scans")
    print(f"   - {len(treatments_db)} traitements")
    print(f"   - {len(appointments_db)} rendez-vous")

if __name__ == "__main__":
    # Créer les données d'exemple au démarrage
    create_sample_data()

    print("\n🚀 Démarrage de l'API de Gestion des Patients...")
    print("📖 Documentation disponible sur: http://localhost:8001/docs")
    print("🔄 API disponible sur: http://localhost:8001")

    # Démarrer le serveur
    uvicorn.run(
        "main_patients_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
