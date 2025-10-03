#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test simple pour vérifier les imports et la structure de base.
"""

def test_basic_imports():
    """Test des imports de base Python."""
    print("🧪 Test des imports de base...")
    
    try:
        import os
        import uuid
        from datetime import datetime, date
        from typing import List, Optional, Dict, Any
        from enum import Enum
        print("✅ Imports Python de base OK")
    except ImportError as e:
        print(f"❌ Erreur imports de base: {e}")
        return False
    
    return True

def test_fastapi_imports():
    """Test des imports FastAPI."""
    print("🧪 Test des imports FastAPI...")
    
    try:
        from fastapi import FastAPI, HTTPException, Query, Depends, status
        from fastapi.middleware.cors import CORSMiddleware
        print("✅ Imports FastAPI OK")
    except ImportError as e:
        print(f"❌ FastAPI non installé: {e}")
        return False
    
    return True

def test_pydantic_imports():
    """Test des imports Pydantic."""
    print("🧪 Test des imports Pydantic...")
    
    try:
        from pydantic import BaseModel, Field, EmailStr, validator
        print("✅ Imports Pydantic OK")
    except ImportError as e:
        print(f"❌ Pydantic non installé: {e}")
        return False
    
    return True

def test_uvicorn_import():
    """Test de l'import Uvicorn."""
    print("🧪 Test de l'import Uvicorn...")
    
    try:
        import uvicorn
        print("✅ Import Uvicorn OK")
    except ImportError as e:
        print(f"❌ Uvicorn non installé: {e}")
        return False
    
    return True

def test_file_structure():
    """Test de la structure des fichiers."""
    print("🧪 Test de la structure des fichiers...")
    
    required_files = [
        "patients_api.py",
        "patients_endpoints.py", 
        "scans_endpoints.py",
        "treatments_endpoints.py",
        "appointments_endpoints.py",
        "main_patients_api.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Fichiers manquants: {missing_files}")
        return False
    else:
        print("✅ Structure des fichiers OK")
        return True

def test_basic_functionality():
    """Test de la fonctionnalité de base."""
    print("🧪 Test de la fonctionnalité de base...")
    
    try:
        # Test des énumérations
        from patients_api import Gender, BloodType, ScanType
        
        # Test de création d'objets
        gender = Gender.MALE
        blood_type = BloodType.A_POSITIVE
        scan_type = ScanType.MRI
        
        print(f"✅ Énumérations OK: {gender}, {blood_type}, {scan_type}")
        
        # Test des fonctions utilitaires
        from patients_api import generate_id, calculate_age
        
        test_id = generate_id()
        test_age = calculate_age("1990-01-01")
        
        print(f"✅ Fonctions utilitaires OK: ID={test_id[:8]}..., Age={test_age}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur fonctionnalité de base: {e}")
        return False

def main():
    """Fonction principale de test."""
    print("=" * 50)
    print("🚀 TEST DE L'API DE GESTION DES PATIENTS")
    print("=" * 50)
    print()
    
    tests = [
        test_basic_imports,
        test_file_structure,
        test_fastapi_imports,
        test_pydantic_imports,
        test_uvicorn_import,
        test_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 RÉSULTATS: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! L'API est prête à démarrer.")
        print()
        print("Pour démarrer l'API:")
        print("python main_patients_api.py")
        print()
        print("Documentation: http://localhost:8001/docs")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les installations.")
        print()
        print("Pour installer les dépendances:")
        print("pip install fastapi uvicorn pydantic[email] email-validator")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
