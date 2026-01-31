"""
Storage Service
Handles file storage and retrieval with encryption
"""

import os
import shutil
from typing import Optional, BinaryIO
from datetime import datetime
import hashlib
from app.config import get_settings
from app.services.encryption_service import get_encryption_service

settings = get_settings()
encryption_service = get_encryption_service()


class StorageService:
    """Service for managing file storage"""
    
    def __init__(self):
        """Initialize storage service"""
        self.upload_dir = settings.UPLOAD_DIR
        self.encrypted_dir = os.path.join(self.upload_dir, "encrypted")
        self.processed_dir = os.path.join(self.upload_dir, "processed")
        
        # Ensure directories exist
        for directory in [self.upload_dir, self.encrypted_dir, self.processed_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def save_file(self, file: BinaryIO, filename: str, encrypt: bool = True) -> dict:
        """
        Save uploaded file
        
        Args:
            file: File object
            filename: Original filename
            encrypt: Whether to encrypt the file
            
        Returns:
            Dictionary with file info
        """
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        
        # Temporary path
        temp_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save file
        with open(temp_path, 'wb') as buffer:
            shutil.copyfileobj(file, buffer)
        
        # Get file size and hash
        file_size = os.path.getsize(temp_path)
        file_hash = self._calculate_file_hash(temp_path)
        
        # Encrypt if requested
        if encrypt:
            encrypted_path = os.path.join(self.encrypted_dir, unique_filename)
            success = encryption_service.encrypt_file(temp_path, encrypted_path)
            
            if success:
                # Remove temp file
                os.unlink(temp_path)
                final_path = encrypted_path
            else:
                raise Exception("File encryption failed")
        else:
            final_path = temp_path
        
        return {
            'filename': filename,
            'stored_filename': unique_filename,
            'path': final_path,
            'size': file_size,
            'hash': file_hash,
            'encrypted': encrypt
        }
    
    def retrieve_file(self, file_path: str, decrypt: bool = True) -> Optional[str]:
        """
        Retrieve file and optionally decrypt
        
        Args:
            file_path: Path to encrypted file
            decrypt: Whether to decrypt the file
            
        Returns:
            Path to decrypted file or None if failed
        """
        if not os.path.exists(file_path):
            return None
        
        if decrypt:
            # Generate temp path for decrypted file
            filename = os.path.basename(file_path)
            temp_path = os.path.join(self.processed_dir, f"temp_{filename}")
            
            success = encryption_service.decrypt_file(file_path, temp_path)
            
            if success:
                return temp_path
            else:
                return None
        else:
            return file_path
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file
        
        Args:
            file_path: Path to file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                return True
            return False
        except Exception as e:
            print(f"File deletion error: {e}")
            return False
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old temporary files
        
        Args:
            max_age_hours: Maximum age of files to keep
            
        Returns:
            Number of files deleted
        """
        deleted_count = 0
        current_time = datetime.utcnow().timestamp()
        max_age_seconds = max_age_hours * 3600
        
        for directory in [self.upload_dir, self.processed_dir]:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                # Skip directories
                if os.path.isdir(file_path):
                    continue
                
                # Check file age
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > max_age_seconds:
                    try:
                        os.unlink(file_path)
                        deleted_count += 1
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
        
        return deleted_count
    
    def get_storage_stats(self) -> dict:
        """
        Get storage statistics
        
        Returns:
            Dictionary with storage stats
        """
        total_size = 0
        file_count = 0
        
        for directory in [self.upload_dir, self.encrypted_dir, self.processed_dir]:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
        
        return {
            'total_files': file_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'total_size_gb': round(total_size / (1024 * 1024 * 1024), 2)
        }
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of file
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of file hash
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read file in chunks
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def verify_file_integrity(self, file_path: str, expected_hash: str) -> bool:
        """
        Verify file integrity using hash
        
        Args:
            file_path: Path to file
            expected_hash: Expected SHA-256 hash
            
        Returns:
            True if hash matches, False otherwise
        """
        actual_hash = self._calculate_file_hash(file_path)
        return actual_hash == expected_hash


# Singleton instance
_storage_service = None


def get_storage_service() -> StorageService:
    """Get or create storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service