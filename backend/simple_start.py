#!/usr/bin/env python3
"""
Script de démarrage simple pour CereBloom
"""

import sys
import os

print("🚀 Démarrage de CereBloom...")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

try:
    print("📦 Import de uvicorn...")
    import uvicorn
    print("✅ uvicorn importé")
    
    print("📦 Import de cerebloom_main...")
    import cerebloom_main
    print("✅ cerebloom_main importé")
    
    print("🌐 Démarrage du serveur sur http://127.0.0.1:8000")
    uvicorn.run(
        "cerebloom_main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
