#!/usr/bin/env python3
"""
Migration: Ajouter la colonne assigned_doctor_id à la table users
Date: 2025-06-01
Description: Ajoute le champ assigned_doctor_id pour permettre l'assignation des secrétaires aux médecins
"""

import asyncio
import asyncpg
import sys
import os
import logging

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_migration():
    """Exécute la migration pour ajouter assigned_doctor_id"""
    
    # Connexion à la base de données
    # Convertir l'URL SQLAlchemy en URL asyncpg
    database_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(database_url)
    
    try:
        logger.info("🔄 Début de la migration: Ajout de assigned_doctor_id")
        
        # Vérifier si la colonne existe déjà
        check_column_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'assigned_doctor_id';
        """
        
        existing_column = await conn.fetchval(check_column_query)
        
        if existing_column:
            logger.info("✅ La colonne assigned_doctor_id existe déjà")
            return
        
        # Ajouter la colonne assigned_doctor_id
        add_column_query = """
        ALTER TABLE users 
        ADD COLUMN assigned_doctor_id VARCHAR(36) NULL;
        """
        
        await conn.execute(add_column_query)
        logger.info("✅ Colonne assigned_doctor_id ajoutée")
        
        # Ajouter l'index sur assigned_doctor_id
        add_index_query = """
        CREATE INDEX IF NOT EXISTS idx_users_assigned_doctor_id 
        ON users(assigned_doctor_id);
        """
        
        await conn.execute(add_index_query)
        logger.info("✅ Index sur assigned_doctor_id créé")
        
        # Ajouter la contrainte de clé étrangère
        add_foreign_key_query = """
        ALTER TABLE users 
        ADD CONSTRAINT fk_users_assigned_doctor_id 
        FOREIGN KEY (assigned_doctor_id) 
        REFERENCES doctors(id) 
        ON DELETE SET NULL;
        """
        
        await conn.execute(add_foreign_key_query)
        logger.info("✅ Contrainte de clé étrangère ajoutée")
        
        # Ajouter un commentaire sur la colonne
        add_comment_query = """
        COMMENT ON COLUMN users.assigned_doctor_id 
        IS 'Pour les secrétaires: médecin assigné';
        """
        
        await conn.execute(add_comment_query)
        logger.info("✅ Commentaire ajouté sur la colonne")
        
        logger.info("🎉 Migration terminée avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la migration: {e}")
        raise
    finally:
        await conn.close()

async def rollback_migration():
    """Rollback de la migration (supprime assigned_doctor_id)"""
    
    # Convertir l'URL SQLAlchemy en URL asyncpg
    database_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(database_url)
    
    try:
        logger.info("🔄 Début du rollback: Suppression de assigned_doctor_id")
        
        # Supprimer la contrainte de clé étrangère
        drop_foreign_key_query = """
        ALTER TABLE users 
        DROP CONSTRAINT IF EXISTS fk_users_assigned_doctor_id;
        """
        
        await conn.execute(drop_foreign_key_query)
        logger.info("✅ Contrainte de clé étrangère supprimée")
        
        # Supprimer l'index
        drop_index_query = """
        DROP INDEX IF EXISTS idx_users_assigned_doctor_id;
        """
        
        await conn.execute(drop_index_query)
        logger.info("✅ Index supprimé")
        
        # Supprimer la colonne
        drop_column_query = """
        ALTER TABLE users 
        DROP COLUMN IF EXISTS assigned_doctor_id;
        """
        
        await conn.execute(drop_column_query)
        logger.info("✅ Colonne assigned_doctor_id supprimée")
        
        logger.info("🎉 Rollback terminé avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du rollback: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("🔄 Exécution du rollback...")
        asyncio.run(rollback_migration())
    else:
        print("🔄 Exécution de la migration...")
        asyncio.run(run_migration())
