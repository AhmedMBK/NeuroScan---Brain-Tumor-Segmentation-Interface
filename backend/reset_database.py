#!/usr/bin/env python3
"""
Script pour réinitialiser la base de données CereBloom
"""

import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from models.database_models import Base

async def reset_database():
    """Supprime et recrée la base de données"""
    
    # Supprimer l'ancien fichier de base de données
    db_file = "cerebloom.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"✅ Ancien fichier {db_file} supprimé")
    
    # Créer le moteur de base de données
    engine = create_async_engine(
        "sqlite+aiosqlite:///./cerebloom.db",
        echo=True
    )
    
    # Créer toutes les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Base de données recréée avec succès !")
    print("✅ Toutes les tables ont été créées")
    
    await engine.dispose()

if __name__ == "__main__":
    print("🔄 Réinitialisation de la base de données CereBloom...")
    asyncio.run(reset_database())
    print("🎉 Terminé ! Vous pouvez maintenant relancer le serveur.")
