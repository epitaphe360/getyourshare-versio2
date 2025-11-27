
import logging
import sys
import json
from datetime import datetime
import os

class JSONFormatter(logging.Formatter):
    """Formatter pour logs en JSON"""
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj)

def setup_logging():
    """Configurer le logging professionnel"""
    
    # Créer le dossier logs si inexistant
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    # Logger racine
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Handler Console (JSON)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # Handler Fichier (Rotation)
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10*1024*1024, # 10MB
        backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Sentry (si configuré)
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[sentry_logging],
            traces_sample_rate=1.0,
            environment=os.getenv("ENV", "development")
        )
        
    return logger

# Initialiser au chargement
logger = setup_logging()
