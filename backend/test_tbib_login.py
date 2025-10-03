#!/usr/bin/env python3
"""
🧪 Test de connexion tbib avec différents mots de passe
"""

import asyncio
import aiohttp
import json

async def test_tbib_login():
    """Test de connexion tbib avec différents mots de passe"""
    
    print("🧪 === TEST CONNEXION TBIB ===")
    
    # Différents mots de passe à tester
    passwords_to_try = [
        "password123",
        "tbib",
        "tbib123",
        "123456",
        "admin123"
    ]
    
    async with aiohttp.ClientSession() as session:
        for password in passwords_to_try:
            print(f"\n🔍 Test avec mot de passe: {password}")
            
            login_data = {
                "email": "tbib@gmail.com",
                "password": password
            }
            
            try:
                async with session.post("http://localhost:8000/api/v1/auth/login", json=login_data) as response:
                    print(f"📊 Statut: {response.status}")
                    
                    if response.status == 200:
                        login_result = await response.json()
                        token = login_result.get("access_token")
                        
                        if token:
                            print(f"✅ SUCCÈS avec mot de passe: {password}")
                            print(f"   Token: {token[:50]}...")
                            
                            # Test de l'endpoint traitements
                            headers = {"Authorization": f"Bearer {token}"}
                            async with session.get("http://localhost:8000/api/v1/treatments", headers=headers) as treatments_response:
                                if treatments_response.status == 200:
                                    treatments_data = await treatments_response.json()
                                    treatments = treatments_data.get("treatments", [])
                                    print(f"   Traitements accessibles: {len(treatments)}")
                                else:
                                    print(f"   ❌ Erreur traitements: {treatments_response.status}")
                            
                            return password  # Retourner le bon mot de passe
                        else:
                            print(f"❌ Pas de token")
                    else:
                        response_text = await response.text()
                        print(f"❌ Échec: {response_text}")
            
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    print(f"\n❌ Aucun mot de passe ne fonctionne pour tbib@gmail.com")
    return None

async def check_user_in_db():
    """Vérifier l'utilisateur tbib dans la base de données"""
    
    print(f"\n🔍 === VÉRIFICATION BASE DE DONNÉES ===")
    
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import select
    from models.database_models import User, Doctor
    from config.settings import Settings
    
    settings = Settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Chercher l'utilisateur tbib
        result = await session.execute(
            select(User.id, User.email, User.role, User.status)
            .where(User.email == "tbib@gmail.com")
        )
        user = result.first()
        
        if user:
            print(f"✅ Utilisateur trouvé:")
            print(f"   - ID: {user.id}")
            print(f"   - Email: {user.email}")
            print(f"   - Rôle: {user.role}")
            print(f"   - Statut: {user.status}")
            
            # Chercher le profil médecin
            result = await session.execute(
                select(Doctor.id, Doctor.first_name, Doctor.last_name)
                .where(Doctor.user_id == user.id)
            )
            doctor = result.first()
            
            if doctor:
                print(f"✅ Profil médecin trouvé:")
                print(f"   - Doctor ID: {doctor.id}")
                print(f"   - Nom: {doctor.first_name} {doctor.last_name}")
            else:
                print(f"❌ Pas de profil médecin trouvé")
        else:
            print(f"❌ Utilisateur tbib@gmail.com non trouvé")

async def main():
    """Test principal"""
    
    # 1. Vérifier la base de données
    await check_user_in_db()
    
    # 2. Tester la connexion
    working_password = await test_tbib_login()
    
    if working_password:
        print(f"\n🎯 === RÉSUMÉ ===")
        print(f"✅ Mot de passe correct pour tbib@gmail.com: {working_password}")
    else:
        print(f"\n🎯 === RÉSUMÉ ===")
        print(f"❌ Impossible de se connecter avec tbib@gmail.com")
        print(f"   Vérifiez que l'utilisateur existe et que le mot de passe est correct")

if __name__ == "__main__":
    asyncio.run(main())
