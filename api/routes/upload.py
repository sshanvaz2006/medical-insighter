"""
Upload Routes
Handles document upload and processing
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.report import MedicalReport, ExtractedEntity, ReportStatus, ReportType
from app.api.routes.auth import get_current_active_user
from app.services.ocr_service import get_ocr_service
from app.services.entity_extraction import get_entity_service
from app.core.security import encrypt_data, encrypt_file
from app.schemas.schemas import UploadResponse, ReportResponse
from app.config import get_settings
import uuid

settings = get_settings()
router = APIRouter(prefix="/upload", tags=["Upload"])

# Get services
ocr_service = get_ocr_service()
entity_service = get_entity_service()


def process_document_background(
    report_id: int,
    file_path: str,
    file_type: str,
    db_session
):
    """Background task to process uploaded document"""
    try:
        # Get report
        report = db_session.query(MedicalReport).filter(
            MedicalReport.id == report_id
        ).first()
        
        if not report:
            return
        
        # Update status
        report.status = ReportStatus.PROCESSING
        db_session.commit()
        
        # Perform OCR
        ocr_result = ocr_service.process_document(file_path, file_type)
        
        if not ocr_result['success']:
            report.status = ReportStatus.FAILED
            report.metadata = {'error': ocr_result.get('error', 'OCR failed')}
            db_session.commit()
            return
        
        # Extract entities
        entities = entity_service.extract_entities(ocr_result['text'])
        entity_summary = entity_service.get_entity_summary(entities)
        
        # Encrypt OCR text
        encrypted_text = encrypt_data(ocr_result['text'])
        
        # Update report
        report.ocr_text = encrypted_text
        report.confidence_score = ocr_result.get('confidence', 0)
        report.processing_time = ocr_result.get('processing_time', 0)
        report.extracted_entities = entities
        report.metadata = {
            'entity_summary': entity_summary,
            'pages': ocr_result.get('pages', 1)
        }
        report.status = ReportStatus.COMPLETED
        
        # Save extracted entities
        for entity_type, entity_list in entities.items():
            for entity_data in entity_list:
                if isinstance(entity_data, dict):
                    extracted_entity = ExtractedEntity(
                        report_id=report_id,
                        entity_type=entity_type,
                        entity_text=entity_data.get('text', ''),
                        normalized_text=entity_service.normalize_entity(
                            entity_data.get('text', ''),
                            entity_type
                        ),
                        confidence=entity_data.get('confidence', 0),
                        context=entity_data.get('context', '')
                    )
                    db_session.add(extracted_entity)
        
        db_session.commit()
        
    except Exception as e:
        print(f"Processing error: {e}")
        if report:
            report.status = ReportStatus.FAILED
            report.metadata = {'error': str(e)}
            db_session.commit()


@router.post("/document", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    patient_name: Optional[str] = Form(None),
    report_type: Optional[ReportType] = Form(ReportType.OTHER),
    report_date: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a medical document for processing
    
    - **file**: Medical document (PDF, JPG, PNG, TIFF)
    - **patient_id**: Patient identifier (optional, encrypted)
    - **patient_name**: Patient name (optional, encrypted)
    - **report_type**: Type of medical report
    - **report_date**: Date of the report
    """
    # Check user permissions
    if not current_user.can_upload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to upload documents"
        )
    
    # Validate file type
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    encrypted_file_path = os.path.join(settings.UPLOAD_DIR, "encrypted", unique_filename)
    
    # Save uploaded file
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Encrypt file
    encrypt_success = encrypt_file(temp_file_path, encrypted_file_path)
    
    if not encrypt_success:
        os.unlink(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encrypt file"
        )
    
    # Parse report date
    parsed_date = None
    if report_date:
        try:
            parsed_date = datetime.fromisoformat(report_date.replace('Z', '+00:00'))
        except:
            pass
    
    # Create database record
    new_report = MedicalReport(
        filename=file.filename,
        file_path=encrypted_file_path,
        file_size=file_size,
        file_type=file_extension,
        report_type=report_type,
        patient_id=encrypt_data(patient_id) if patient_id else None,
        patient_name=encrypt_data(patient_name) if patient_name else None,
        report_date=parsed_date,
        status=ReportStatus.PENDING,
        uploaded_by=current_user.id,
        is_encrypted=True
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    # Process document in background
    background_tasks.add_task(
        process_document_background,
        new_report.id,
        temp_file_path,
        file_extension,
        db
    )
    
    return UploadResponse(
        report_id=new_report.id,
        filename=file.filename,
        status="pending",
        message="Document uploaded successfully and is being processed"
    )


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def upload_batch_documents(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload multiple documents at once
    """
    if not current_user.can_upload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to upload documents"
        )
    
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files per batch"
        )
    
    results = []
    
    for file in files:
        try:
            # Process each file
            file_extension = file.filename.split('.')[-1].lower()
            
            if file_extension not in settings.ALLOWED_EXTENSIONS:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": "File type not allowed"
                })
                continue
            
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            temp_file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
            encrypted_file_path = os.path.join(settings.UPLOAD_DIR, "encrypted", unique_filename)
            
            # Save and encrypt
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file.file.seek(0, 2)
            file_size = file.file.tell()
            
            encrypt_file(temp_file_path, encrypted_file_path)
            
            # Create record
            new_report = MedicalReport(
                filename=file.filename,
                file_path=encrypted_file_path,
                file_size=file_size,
                file_type=file_extension,
                status=ReportStatus.PENDING,
                uploaded_by=current_user.id,
                is_encrypted=True
            )
            
            db.add(new_report)
            db.commit()
            db.refresh(new_report)
            
            # Process in background
            background_tasks.add_task(
                process_document_background,
                new_report.id,
                temp_file_path,
                file_extension,
                db
            )
            
            results.append({
                "filename": file.filename,
                "report_id": new_report.id,
                "status": "pending",
                "message": "Uploaded successfully"
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })
    
    return {"results": results}