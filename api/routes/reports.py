"""
Medical Report Model
Database model for storing medical reports and extracted data
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class ReportStatus(str, enum.Enum):
    """Report processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportType(str, enum.Enum):
    """Medical report types"""
    LAB_REPORT = "lab_report"
    RADIOLOGY = "radiology"
    PATHOLOGY = "pathology"
    PRESCRIPTION = "prescription"
    DISCHARGE_SUMMARY = "discharge_summary"
    CONSULTATION = "consultation"
    OTHER = "other"


class MedicalReport(Base):
    """Medical report model with encrypted storage"""
    __tablename__ = "medical_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # File Information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Encrypted file path
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    
    # Report Metadata
    report_type = Column(Enum(ReportType), default=ReportType.OTHER)
    patient_id = Column(String(100), index=True)  # Encrypted
    patient_name = Column(String(255))  # Encrypted
    report_date = Column(DateTime)
    
    # Processing
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, index=True)
    ocr_text = Column(Text)  # Encrypted extracted text
    confidence_score = Column(Float)
    processing_time = Column(Float)  # Time in seconds
    
    # Structured Data (encrypted JSON)
    extracted_entities = Column(JSON)  # Medical entities
    metadata = Column(JSON)  # Additional metadata
    
    # Audit
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accessed_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)
    
    # Security
    is_encrypted = Column(Boolean, default=True, nullable=False)
    encryption_version = Column(String(10), default="1.0")
    
    # Relationships
    uploaded_by_user = relationship("User", back_populates="reports")
    entities = relationship("ExtractedEntity", back_populates="report", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MedicalReport {self.id} - {self.filename}>"


class ExtractedEntity(Base):
    """Extracted medical entities from reports"""
    __tablename__ = "extracted_entities"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("medical_reports.id"), nullable=False, index=True)
    
    # Entity Information
    entity_type = Column(String(50), nullable=False, index=True)  # disease, medication, test, etc.
    entity_text = Column(String(500), nullable=False)
    normalized_text = Column(String(500))  # Standardized form
    
    # Context
    context = Column(Text)  # Surrounding text
    start_pos = Column(Integer)
    end_pos = Column(Integer)
    
    # Confidence
    confidence = Column(Float)
    
    # Medical Codes (if available)
    icd_code = Column(String(20))  # ICD-10 code
    snomed_code = Column(String(50))  # SNOMED CT code
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    report = relationship("MedicalReport", back_populates="entities")
    
    def __repr__(self):
        return f"<Entity {self.entity_type}: {self.entity_text}>"


class AuditLog(Base):
    """Audit log for compliance and security"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Action Details
    action = Column(String(100), nullable=False, index=True)  # view, edit, delete, etc.
    resource_type = Column(String(50), nullable=False)  # report, user, etc.
    resource_id = Column(Integer)
    
    # Request Details
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Additional Data
    details = Column(JSON)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.action} by user {self.user_id}>"