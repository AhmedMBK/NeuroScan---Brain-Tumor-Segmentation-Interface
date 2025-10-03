"""
🧠 CereBloom - Configuration du Logger
Système de logging centralisé pour l'application
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from config.settings import settings

def setup_logger(name: str = None) -> logging.Logger:
    """Configure et retourne un logger"""
    
    # Création du dossier de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configuration du logger
    logger = logging.getLogger(name or __name__)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Éviter la duplication des handlers
    if logger.handlers:
        return logger
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler pour le fichier avec rotation
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Logger principal de l'application
app_logger = setup_logger("cerebloom")
