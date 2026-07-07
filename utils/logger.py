import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from config import LOGS_DIR

def setup_logger():
    # Ensure logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("UUIDGeneratorPro")
    logger.setLevel(logging.DEBUG)
    
    # Prevent adding handlers multiple times
    if not logger.handlers:
        # File handler (rotates at 5MB, keeps 5 backups)
        log_filename = LOGS_DIR / f"app_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = RotatingFileHandler(
            log_filename, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

logger = setup_logger()
