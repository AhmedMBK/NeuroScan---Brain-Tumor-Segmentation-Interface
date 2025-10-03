#!/usr/bin/env python3
"""
Script pour déboguer les tokens JWT
"""

import jwt
import sys
import os
import logging

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def decode_token(token_string):
    """Décode un token JWT"""
    
    try:
        logger.info("🔍 Décodage du token JWT...")
        
        # Décoder sans vérification de signature pour le débogage
        decoded = jwt.decode(token_string, options={"verify_signature": False})
        
        logger.info("✅ Token décodé avec succès:")
        logger.info(f"   👤 User ID: {decoded.get('sub', 'Non trouvé')}")
        logger.info(f"   📧 Email: {decoded.get('email', 'Non trouvé')}")
        logger.info(f"   🎭 Rôle: {decoded.get('role', 'Non trouvé')}")
        logger.info(f"   ⏰ Expiration: {decoded.get('exp', 'Non trouvé')}")
        logger.info(f"   🕐 Émis à: {decoded.get('iat', 'Non trouvé')}")
        
        # Vérifier si le token est expiré
        import time
        current_time = int(time.time())
        exp_time = decoded.get('exp', 0)
        
        if exp_time and current_time > exp_time:
            logger.warning("⚠️  Token expiré!")
        else:
            logger.info("✅ Token valide (non expiré)")
        
        return decoded
        
    except jwt.InvalidTokenError as e:
        logger.error(f"❌ Erreur de décodage du token: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_token.py <token>")
        print("Exemple: python debug_token.py eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        sys.exit(1)
    
    token = sys.argv[1]
    decode_token(token)
