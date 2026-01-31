"""
Security Module
Handles authentication, password hashing, JWT tokens, and encryption
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.config import get_settings
import base64
import secrets

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption (AES-256 via Fernet)
cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode() if len(settings.ENCRYPTION_KEY) == 44 else base64.urlsafe_b64encode(settings.ENCRYPTION_KEY.encode()[:32]))


# Password functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


# JWT Token functions
def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": secrets.token_urlsafe(32)  # Unique token ID
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[Dict]:
    """Verify token and check type"""
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    if payload.get("type") != token_type:
        return None
    
    return payload


# Data Encryption functions (for HIPAA compliance)
def encrypt_data(data: str) -> str:
    """Encrypt sensitive data using AES-256"""
    if not data:
        return ""
    
    encrypted = cipher_suite.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return ""
    
    try:
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = cipher_suite.decrypt(decoded)
        return decrypted.decode()
    except Exception:
        return ""


def encrypt_file(file_path: str, output_path: str) -> bool:
    """Encrypt a file"""
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        encrypted_data = cipher_suite.encrypt(file_data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
        
        return True
    except Exception as e:
        print(f"Encryption error: {e}")
        return False


def decrypt_file(encrypted_path: str, output_path: str) -> bool:
    """Decrypt a file"""
    try:
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        return True
    except Exception as e:
        print(f"Decryption error: {e}")
        return False


# API Key generation (for external integrations)
def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


# Password validation
def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"