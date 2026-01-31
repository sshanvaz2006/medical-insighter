"""
Encryption Service
Handles data encryption/decryption for HIPAA compliance
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Optional
from app.config import get_settings

settings = get_settings()


class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        """Initialize encryption service with key from settings"""
        # Use the encryption key from settings
        key = settings.ENCRYPTION_KEY.encode()
        
        # Ensure key is proper length for Fernet (44 bytes base64)
        if len(key) == 44:
            self.cipher = Fernet(key)
        else:
            # Derive proper key if needed
            self.cipher = Fernet(base64.urlsafe_b64encode(key[:32]))
    
    def encrypt_text(self, plaintext: str) -> str:
        """
        Encrypt text data
        
        Args:
            plaintext: Text to encrypt
            
        Returns:
            Base64 encoded encrypted text
        """
        if not plaintext:
            return ""
        
        try:
            encrypted = self.cipher.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt_text(self, encrypted_text: str) -> str:
        """
        Decrypt text data
        
        Args:
            encrypted_text: Base64 encoded encrypted text
            
        Returns:
            Decrypted plaintext
        """
        if not encrypted_text:
            return ""
        
        try:
            decoded = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_file(self, input_path: str, output_path: str) -> bool:
        """
        Encrypt a file
        
        Args:
            input_path: Path to plaintext file
            output_path: Path to save encrypted file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(input_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = self.cipher.encrypt(file_data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"File encryption error: {e}")
            return False
    
    def decrypt_file(self, encrypted_path: str, output_path: str) -> bool:
        """
        Decrypt a file
        
        Args:
            encrypted_path: Path to encrypted file
            output_path: Path to save decrypted file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return True
        except Exception as e:
            print(f"File decryption error: {e}")
            return False
    
    def encrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Encrypt specific fields in a dictionary
        
        Args:
            data: Dictionary to encrypt
            fields: List of field names to encrypt
            
        Returns:
            Dictionary with encrypted fields
        """
        encrypted_data = data.copy()
        
        for field in fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt_text(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields: list) -> dict:
        """
        Decrypt specific fields in a dictionary
        
        Args:
            data: Dictionary to decrypt
            fields: List of field names to decrypt
            
        Returns:
            Dictionary with decrypted fields
        """
        decrypted_data = data.copy()
        
        for field in fields:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_data[field] = self.decrypt_text(decrypted_data[field])
        
        return decrypted_data
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key
        
        Returns:
            Base64 encoded Fernet key
        """
        return Fernet.generate_key().decode()
    
    @staticmethod
    def hash_data(data: str, salt: Optional[bytes] = None) -> tuple:
        """
        Create a one-way hash of data (for de-identification)
        
        Args:
            data: Data to hash
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (hash, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(data.encode())
        hash_value = base64.urlsafe_b64encode(key).decode()
        salt_value = base64.urlsafe_b64encode(salt).decode()
        
        return hash_value, salt_value


# Singleton instance
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """Get or create encryption service instance"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service