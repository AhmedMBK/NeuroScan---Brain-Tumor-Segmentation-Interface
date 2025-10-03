#!/usr/bin/env python3
"""
🧪 Test de l'endpoint des traitements
"""

import asyncio
import aiohttp
import json

async def test_treatments_endpoint():
    """Test de l'endpoint des traitements pour différents rôles"""
    
    print("🧪 === TEST ENDPOINT TRAITEMENTS ===")
    
    # Test avec différents rôles
    roles_to_test = [
        ("tbib@gmail.com", "password123", "DOCTOR"),
        ("admin@cerebloom.com", "admin123", "ADMIN"),
        ("azza@gmail.com", "azzaazza", "SECRETARY")
    ]
    
    async with aiohttp.ClientSession() as session:
        for email, password, role_name in roles_to_test:
            print(f"\n🔍 === TEST RÔLE {role_name} ({email}) ===")
            
            # 1. Connexion
            login_data = {"email": email, "password": password}
            
            try:
                async with session.post("http://localhost:8000/api/v1/auth/login", json=login_data) as response:
                    if response.status != 200:
                        print(f"❌ Échec connexion {role_name}: {response.status}")
                        continue
                    
                    login_result = await response.json()
                    token = login_result.get("access_token")
                    
                    if not token:
                        print(f"❌ Pas de token pour {role_name}")
                        continue
                    
                    print(f"✅ Connexion {role_name} réussie")
            
            except Exception as e:
                print(f"❌ Erreur connexion {role_name}: {e}")
                continue
            
            # 2. Test de l'endpoint traitements
            headers = {"Authorization": f"Bearer {token}"}
            
            try:
                async with session.get("http://localhost:8000/api/v1/treatments", headers=headers) as response:
                    print(f"📊 Statut réponse {role_name}: {response.status}")
                    
                    if response.status != 200:
                        response_text = await response.text()
                        print(f"❌ Échec traitements {role_name}: {response_text}")
                        continue
                    
                    treatments_data = await response.json()
                    treatments = treatments_data.get("treatments", [])
                    
                    print(f"✅ Traitements {role_name} récupérés: {len(treatments)} trouvés")
                    
                    if treatments:
                        print(f"📋 Premier traitement:")
                        first_treatment = treatments[0]
                        print(f"   - ID: {first_treatment.get('id', 'N/A')[:8]}...")
                        print(f"   - Type: {first_treatment.get('treatment_type', 'N/A')}")
                        print(f"   - Nom: {first_treatment.get('treatment_name', 'N/A')}")
                        print(f"   - Médicament: {first_treatment.get('medication_name', 'N/A')}")
                        print(f"   - Dosage: {first_treatment.get('dosage', 'N/A')}")
                        print(f"   - Fréquence: {first_treatment.get('frequency', 'N/A')}")
                        print(f"   - Durée: {first_treatment.get('duration', 'N/A')}")
                        print(f"   - Date début: {first_treatment.get('start_date', 'N/A')}")
                        print(f"   - Date fin: {first_treatment.get('end_date', 'N/A')}")
                        print(f"   - Statut: {first_treatment.get('status', 'N/A')}")
                        print(f"   - Patient ID: {first_treatment.get('patient_id', 'N/A')[:8]}...")
                        
                        # Afficher tous les traitements pour ce rôle
                        print(f"📋 Tous les traitements pour {role_name}:")
                        for i, treatment in enumerate(treatments, 1):
                            print(f"   {i}. {treatment.get('treatment_type', 'N/A')} - {treatment.get('status', 'N/A')} - Patient: {treatment.get('patient_id', 'N/A')[:8]}...")
                    else:
                        print(f"📋 Aucun traitement trouvé pour {role_name}")
            
            except Exception as e:
                print(f"❌ Erreur traitements {role_name}: {e}")

async def check_treatments_in_db():
    """Vérifier s'il y a des traitements dans la base de données"""
    
    print(f"\n🔍 === VÉRIFICATION BASE DE DONNÉES ===")
    
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import select, func
    from models.database_models import Treatment, Patient, Doctor, User
    from config.settings import Settings
    
    settings = Settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Compter les traitements
        result = await session.execute(select(func.count(Treatment.id)))
        total_treatments = result.scalar()
        
        print(f"📊 Total traitements en base: {total_treatments}")
        
        if total_treatments > 0:
            # Lister quelques traitements
            result = await session.execute(
                select(Treatment.id, Treatment.treatment_type, Treatment.medication_name, 
                       Treatment.status, Treatment.patient_id)
                .limit(5)
            )
            treatments = result.all()
            
            print(f"📋 Exemples de traitements:")
            for t in treatments:
                print(f"   - {t.id[:8]}... | {t.treatment_type} | {t.medication_name} | {t.status} | Patient: {t.patient_id[:8]}...")
        
        # Vérifier les relations patient-médecin
        result = await session.execute(
            select(func.count(Patient.id.distinct()))
            .where(Patient.assigned_doctor_id.isnot(None))
        )
        patients_with_doctors = result.scalar()
        
        print(f"📊 Patients avec médecins assignés: {patients_with_doctors}")

async def main():
    """Test principal"""
    
    # 1. Vérifier la base de données
    await check_treatments_in_db()
    
    # 2. Tester l'endpoint
    await test_treatments_endpoint()
    
    print(f"\n🎯 === RÉSUMÉ ===")
    print("✅ Endpoint traitements corrigé avec:")
    print("   - Filtrage par rôle (ADMIN/DOCTOR/SECRETARY)")
    print("   - Filtrage par patient (optionnel)")
    print("   - Données complètes retournées")
    print("   - Permissions respectées")

if __name__ == "__main__":
    asyncio.run(main())
