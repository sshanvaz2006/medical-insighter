"""
User Model
Database model for user accounts with role-based access control
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    STAFF = "staff"
    VIEWER = "viewer"


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STAFF, nullable=False)
    department = Column(String(100))
    phone = Column(String(20))
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    reports = relationship("MedicalReport", back_populates="uploaded_by_user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
    
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_superuser
    
    @property
    def can_upload(self):
        return self.role in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE, UserRole.STAFF]
    
    @property
    def can_view_analytics(self):
        return self.role in [UserRole.ADMIN, UserRole.DOCTOR]


class RefreshToken(Base):
    """Refresh tokens for JWT authentication"""
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<RefreshToken user_id={self.user_id}>"