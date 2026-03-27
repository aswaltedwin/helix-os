import logging
import sys
from datetime import datetime

class LogfmtFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created).isoformat()
        level = record.levelname.lower()
        msg = record.getMessage()
        return f'time="{timestamp}" level={level} msg="{msg}"'

def setup_logging():
    """Configure structured logging for HelixOS"""
    
    # Console handler with Logfmt-style formatter
    logHandler = logging.StreamHandler(sys.stdout)
    formatter = LogfmtFormatter()
    logHandler.setFormatter(formatter)


    
    # Root logger
    root_logger = logging.getLogger()
    
    # Avoid adding multiple handlers if already configured
    if not root_logger.handlers:
        root_logger.addHandler(logHandler)
        root_logger.setLevel(logging.INFO)

    
    # Suppress verbose logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.INFO)
    
    return root_logger

logger = setup_logging()