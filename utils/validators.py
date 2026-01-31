"""
Validators
Input validation utilities
"""

import re
from typing import List, Tuple
from email_validator import validate_email as email_validate, EmailNotValidError


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        # Validate email
        valid = email_validate(email)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)


def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file type by extension
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (without dots)
        
    Returns:
        True if valid, False otherwise
    """
    if not filename:
        return False
    
    # Get file extension
    extension = filename.split('.')[-1].lower()
    
    return extension in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_size: int, max_size: int) -> bool:
    """
    Validate file size
    
    Args:
        file_size: Size of file in bytes
        max_size: Maximum allowed size in bytes
        
    Returns:
        True if valid, False otherwise
    """
    return 0 < file_size <= max_size


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent security issues
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename


def validate_patient_id(patient_id: str) -> Tuple[bool, str]:
    """
    Validate patient ID format
    
    Args:
        patient_id: Patient identifier
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not patient_id:
        return False, "Patient ID cannot be empty"
    
    # Check length
    if len(patient_id) < 3 or len(patient_id) > 50:
        return False, "Patient ID must be between 3 and 50 characters"
    
    # Check format (alphanumeric with dashes/underscores)
    if not re.match(r'^[a-zA-Z0-9_-]+$', patient_id):
        return False, "Patient ID can only contain letters, numbers, dashes, and underscores"
    
    return True, "Valid patient ID"


def validate_phone_number(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number
    
    Args:
        phone: Phone number
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not phone:
        return False, "Phone number cannot be empty"
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it's all digits and reasonable length
    if not cleaned.isdigit():
        return False, "Phone number must contain only digits"
    
    if len(cleaned) < 10 or len(cleaned) > 15:
        return False, "Phone number must be between 10 and 15 digits"
    
    return True, "Valid phone number"


def validate_date_format(date_string: str) -> Tuple[bool, str]:
    """
    Validate date string format (ISO 8601)
    
    Args:
        date_string: Date string
        
    Returns:
        Tuple of (is_valid, message)
    """
    from datetime import datetime
    
    if not date_string:
        return False, "Date cannot be empty"
    
    # Try to parse ISO format
    try:
        datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return True, "Valid date format"
    except ValueError:
        return False, "Invalid date format. Use ISO 8601 format (YYYY-MM-DD)"


def validate_password_complexity(password: str) -> Tuple[bool, List[str]]:
    """
    Validate password complexity
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        issues.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        issues.append("Password must contain at least one special character")
    
    # Check for common patterns
    common_passwords = ['password', '12345678', 'qwerty', 'admin', 'letmein']
    if password.lower() in common_passwords:
        issues.append("Password is too common")
    
    return len(issues) == 0, issues


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) < 3 or len(username) > 50:
        return False, "Username must be between 3 and 50 characters"
    
    # Alphanumeric with underscores and hyphens
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    # Must start with a letter
    if not username[0].isalpha():
        return False, "Username must start with a letter"
    
    return True, "Valid username"


def sanitize_html(text: str) -> str:
    """
    Remove HTML tags from text
    
    Args:
        text: Text potentially containing HTML
        
    Returns:
        Text with HTML tags removed
    """
    import html
    
    # Unescape HTML entities
    text = html.unescape(text)
    
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    
    return clean.strip()


def validate_json_structure(data: dict, required_fields: List[str]) -> Tuple[bool, str]:
    """
    Validate JSON structure has required fields
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, message)
    """
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, "All required fields present"