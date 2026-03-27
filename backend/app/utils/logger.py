import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured logging for HelixOS"""
    
    # Console handler with JSON formatter
    logHandler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s',
        timestamp=True
    )
    logHandler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(logHandler)
    root_logger.setLevel(logging.INFO)
    
    # Suppress verbose logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.INFO)
    
    return root_logger

logger = setup_logging()