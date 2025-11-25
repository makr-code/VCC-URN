"""
Structured logging configuration for VCC-URN
Phase 1: Production Hardening
"""
import logging
import sys
from pythonjsonlogger import jsonlogger

from vcc_urn.core.config import settings


def setup_logging():
    """Configure structured logging based on settings"""
    logger = logging.getLogger()
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Configure formatter based on log_format
    if settings.log_format == "json":
        # JSON formatter for production
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            rename_fields={
                'asctime': 'timestamp',
                'name': 'logger',
                'levelname': 'level',
                'message': 'msg'
            }
        )
    else:
        # Text formatter for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    return logger


# Initialize logger
logger = setup_logging()
