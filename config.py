"""
Core Configuration Module
Handles all application settings and environment variables
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application Settings"""
    
    # Application
    APP_NAME: str = "Medical Insight Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = Field(..., min_length=32)
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_EXPIRE: int = 3600
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "jpg", "jpeg", "png", "tiff"]
    
    # OCR
    OCR_LANGUAGES: List[str] = ["en"]
    OCR_GPU: bool = False
    OCR_BATCH_SIZE: int = 4
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@medicalinsight.com"
    
    # Audit
    ENABLE_AUDIT_LOG: bool = True
    AUDIT_LOG_FILE: str = "logs/audit.log"
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_EXTENSIONS", pre=True)
    def parse_allowed_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    @validator("OCR_LANGUAGES", pre=True)
    def parse_ocr_languages(cls, v):
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create necessary directories
def create_directories():
    """Create required directories if they don't exist"""
    settings = get_settings()
    directories = [
        settings.UPLOAD_DIR,
        os.path.dirname(settings.LOG_FILE),
        os.path.dirname(settings.AUDIT_LOG_FILE),
        os.path.join(settings.UPLOAD_DIR, "encrypted"),
        os.path.join(settings.UPLOAD_DIR, "processed"),
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Initialize on import
create_directories()