#!/usr/bin/env python3
"""
🐘 CereBloom - Migration vers PostgreSQL
Script pour migrer de SQLite vers PostgreSQL
"""

import asyncio
import os
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
sys.path.insert(0, str(Path(__file__).parent))

async def setup_postgresql():
    """Configure PostgreSQL pour CereBloom"""
    print("🐘 MIGRATION CEREBLOOM VERS POSTGRESQL")
    print("=" * 50)
    
    # 1. Vérifier les dépendances
    print("🔍 Vérification des dépendances...")
    
    try:
        import asyncpg
        print("✅ asyncpg installé")
    except ImportError:
        print("❌ asyncpg manquant")
        print("   Installez avec: pip install asyncpg")
        return False
    
    try:
        import psycopg2
        print("✅ psycopg2 installé")
    except ImportError:
        print("⚠️ psycopg2 manquant (optionnel)")
        print("   Installez avec: pip install psycopg2-binary")
    
    # 2. Configuration de la base de données
    print("\n🔧 Configuration PostgreSQL...")
    
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "cerebloom_db",
        "user": "cerebloom_user",
        "password": "cerebloom_password"
    }
    
    print(f"   Host: {db_config['host']}")
    print(f"   Port: {db_config['port']}")
    print(f"   Database: {db_config['database']}")
    print(f"   User: {db_config['user']}")
    
    # 3. Test de connexion
    print("\n🔗 Test de connexion...")
    
    try:
        # Connexion à la base postgres par défaut pour créer la DB
        conn = await asyncpg.connect(
            host=db_config["host"],
            port=db_config["port"],
            user="postgres",  # Utilisateur admin par défaut
            password="postgres",  # Mot de passe admin
            database="postgres"
        )
        
        print("✅ Connexion PostgreSQL réussie")
        
        # 4. Créer l'utilisateur et la base de données
        print("\n🏗️ Création de la base de données...")
        
        try:
            # Créer l'utilisateur
            await conn.execute(f"""
                CREATE USER {db_config['user']} WITH PASSWORD '{db_config['password']}';
            """)
            print(f"✅ Utilisateur {db_config['user']} créé")
        except Exception as e:
            if "already exists" in str(e):
                print(f"⚠️ Utilisateur {db_config['user']} existe déjà")
            else:
                print(f"❌ Erreur création utilisateur: {e}")
        
        try:
            # Créer la base de données
            await conn.execute(f"""
                CREATE DATABASE {db_config['database']} OWNER {db_config['user']};
            """)
            print(f"✅ Base de données {db_config['database']} créée")
        except Exception as e:
            if "already exists" in str(e):
                print(f"⚠️ Base de données {db_config['database']} existe déjà")
            else:
                print(f"❌ Erreur création base: {e}")
        
        # Donner les permissions
        await conn.execute(f"""
            GRANT ALL PRIVILEGES ON DATABASE {db_config['database']} TO {db_config['user']};
        """)
        
        await conn.close()
        
        # 5. Test de connexion à la nouvelle base
        print("\n🧪 Test de la nouvelle base...")
        
        app_conn = await asyncpg.connect(
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
        )
        
        # Test simple
        result = await app_conn.fetchval("SELECT version();")
        print(f"✅ PostgreSQL version: {result[:50]}...")
        
        await app_conn.close()
        
        # 6. Copier la configuration
        print("\n📋 Configuration des fichiers...")
        
        env_source = Path(".env.postgres")
        env_target = Path(".env")
        
        if env_source.exists():
            # Sauvegarder l'ancien .env
            if env_target.exists():
                backup_path = Path(".env.sqlite.backup")
                env_target.rename(backup_path)
                print(f"✅ Ancien .env sauvegardé vers {backup_path}")
            
            # Copier la nouvelle configuration
            env_target.write_text(env_source.read_text())
            print(f"✅ Configuration PostgreSQL activée dans .env")
        
        print("\n🎉 MIGRATION TERMINÉE AVEC SUCCÈS !")
        print("=" * 50)
        print("📋 Prochaines étapes:")
        print("1. Redémarrez le serveur: python cerebloom_main.py")
        print("2. Les tables seront créées automatiquement")
        print("3. Testez avec: http://localhost:8000/docs")
        print("4. Créez un nouvel utilisateur admin")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion PostgreSQL: {e}")
        print("\n🔧 Solutions possibles:")
        print("1. Vérifiez que PostgreSQL est installé et démarré")
        print("2. Vérifiez les identifiants (postgres/postgres par défaut)")
        print("3. Installez PostgreSQL: https://www.postgresql.org/download/")
        return False

async def rollback_to_sqlite():
    """Revenir à SQLite"""
    print("🔄 RETOUR À SQLITE")
    print("=" * 30)
    
    backup_path = Path(".env.sqlite.backup")
    env_path = Path(".env")
    
    if backup_path.exists():
        env_path.write_text(backup_path.read_text())
        print("✅ Configuration SQLite restaurée")
        return True
    else:
        print("❌ Pas de sauvegarde SQLite trouvée")
        return False

async def main():
    """Menu principal"""
    print("🧠 CereBloom - Migration Base de Données")
    print("=" * 40)
    print("1. Migrer vers PostgreSQL")
    print("2. Revenir à SQLite")
    print("3. Quitter")
    
    choice = input("\nVotre choix (1-3): ").strip()
    
    if choice == "1":
        await setup_postgresql()
    elif choice == "2":
        await rollback_to_sqlite()
    elif choice == "3":
        print("👋 Au revoir !")
    else:
        print("❌ Choix invalide")

if __name__ == "__main__":
    asyncio.run(main())
