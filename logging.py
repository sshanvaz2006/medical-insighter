"""
Logging Configuration
Structured logging with JSON format for production
"""

import logging
import sys
from datetime import datetime
from pythonjsonlogger import jsonlogger
from app.config import get_settings

settings = get_settings()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
        
        # Add application name
        log_record['app'] = settings.APP_NAME


def setup_logging():
    """
    Setup application logging
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    if settings.ENVIRONMENT == "production":
        # Use JSON formatter for production
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        # Use simple formatter for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    try:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create file handler: {e}")
    
    return logger


def setup_audit_logging():
    """
    Setup audit logging for HIPAA compliance
    """
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False
    
    # Remove existing handlers
    audit_logger.handlers = []
    
    # Audit file handler
    try:
        audit_handler = logging.FileHandler(settings.AUDIT_LOG_FILE)
        audit_handler.setLevel(logging.INFO)
        
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(message)s %(user_id)s %(action)s %(resource)s'
        )
        audit_handler.setFormatter(formatter)
        
        audit_logger.addHandler(audit_handler)
    except Exception as e:
        logging.warning(f"Could not create audit log handler: {e}")
    
    return audit_logger


def log_audit(user_id: int, action: str, resource_type: str, resource_id: int = None, details: dict = None):
    """
    Log an audit event
    
    Args:
        user_id: ID of the user performing the action
        action: Action performed (view, create, update, delete, etc.)
        resource_type: Type of resource (report, user, etc.)
        resource_id: ID of the resource
        details: Additional details
    """
    audit_logger = logging.getLogger('audit')
    
    audit_logger.info(
        f"User {user_id} performed {action} on {resource_type}",
        extra={
            'user_id': user_id,
            'action': action,
            'resource': resource_type,
            'resource_id': resource_id,
            'details': details or {}
        }
    )


# Initialize logging on import
app_logger = setup_logging()
audit_logger = setup_audit_logging()