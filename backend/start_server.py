#!/usr/bin/env python3
"""
Script de lancement simple pour CereBloom Backend
"""

import uvicorn
import os
import sys

if __name__ == "__main__":
    print("🚀 Démarrage de CereBloom Backend...")
    
    # Configuration d'uvicorn
    config = {
        "app": "cerebloom_main:app",
        "host": "127.0.0.1",
        "port": 8000,
        "reload": True,
        "log_level": "info"
    }
    
    try:
        uvicorn.run(**config)
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        sys.exit(1)
