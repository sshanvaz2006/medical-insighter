"""
Analytics Routes
Provides analytics and insights on medical reports
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import Counter
from app.database import get_db
from app.models.user import User
from app.models.report import MedicalReport, ExtractedEntity, ReportStatus, ReportType
from app.api.routes.auth import get_current_active_user
from app.schemas.schemas import (
    TrendAnalysisRequest, TrendAnalysisResponse, TrendDataPoint,
    DashboardStats, ReportResponse
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics and recent reports
    """
    if not current_user.can_view_analytics:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view analytics"
        )
    
    # Base query
    query = db.query(MedicalReport)
    if not current_user.is_admin:
        query = query.filter(MedicalReport.uploaded_by == current_user.id)
    
    # Total reports
    total_reports = query.count()
    
    # Reports this month
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    reports_this_month = query.filter(
        MedicalReport.created_at >= first_day_of_month
    ).count()
    
    # Processing reports
    processing_reports = query.filter(
        MedicalReport.status == ReportStatus.PROCESSING
    ).count()
    
    # Total unique patients
    total_patients = query.filter(
        MedicalReport.patient_id.isnot(None)
    ).distinct(MedicalReport.patient_id).count()
    
    # Recent reports
    recent_reports = query.order_by(desc(MedicalReport.created_at)).limit(5).all()
    
    # Top diagnoses (from entities)
    entity_query = db.query(
        ExtractedEntity.entity_text,
        func.count(ExtractedEntity.id).label('count')
    ).filter(
        ExtractedEntity.entity_type == 'disease'
    )
    
    if not current_user.is_admin:
        entity_query = entity_query.join(MedicalReport).filter(
            MedicalReport.uploaded_by == current_user.id
        )
    
    top_diagnoses = entity_query.group_by(
        ExtractedEntity.entity_text
    ).order_by(desc('count')).limit(10).all()
    
    top_diagnoses_list = [
        {"name": text, "count": count} for text, count in top_diagnoses
    ]
    
    # Report types distribution
    report_types = query.with_entities(
        MedicalReport.report_type,
        func.count(MedicalReport.id).label('count')
    ).group_by(MedicalReport.report_type).all()
    
    report_types_dict = {
        report_type.value: count for report_type, count in report_types
    }
    
    return DashboardStats(
        total_reports=total_reports,
        reports_this_month=reports_this_month,
        total_patients=total_patients,
        processing_reports=processing_reports,
        recent_reports=recent_reports,
        top_diagnoses=top_diagnoses_list,
        report_types_distribution=report_types_dict
    )


@router.post("/trends", response_model=TrendAnalysisResponse)
async def get_trend_analysis(
    params: TrendAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get trend analysis for entities over time
    """
    if not current_user.can_view_analytics:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view analytics"
        )
    
    # Date range
    date_from = params.date_from or (datetime.utcnow() - timedelta(days=90))
    date_to = params.date_to or datetime.utcnow()
    
    # Base query
    query = db.query(
        ExtractedEntity,
        MedicalReport.created_at
    ).join(MedicalReport)
    
    if not current_user.is_admin:
        query = query.filter(MedicalReport.uploaded_by == current_user.id)
    
    # Filter by entity type
    if params.entity_type:
        query = query.filter(ExtractedEntity.entity_type == params.entity_type.value)
    
    # Filter by date range
    query = query.filter(
        MedicalReport.created_at >= date_from,
        MedicalReport.created_at <= date_to
    )
    
    results = query.all()
    
    # Group by time period
    data_points = {}
    entity_counter = Counter()
    
    for entity, created_at in results:
        # Format date based on group_by parameter
        if params.group_by == "day":
            date_key = created_at.strftime("%Y-%m-%d")
        elif params.group_by == "week":
            date_key = created_at.strftime("%Y-W%U")
        elif params.group_by == "month":
            date_key = created_at.strftime("%Y-%m")
        else:  # year
            date_key = created_at.strftime("%Y")
        
        # Initialize data point if needed
        if date_key not in data_points:
            data_points[date_key] = {
                'count': 0,
                'entities': []
            }
        
        # Increment count
        data_points[date_key]['count'] += 1
        data_points[date_key]['entities'].append(entity.entity_text)
        
        # Track top entities
        entity_counter[entity.entity_text] += 1
    
    # Convert to list
    trend_data = [
        TrendDataPoint(
            date=date,
            count=data['count'],
            entities=list(set(data['entities']))
        )
        for date, data in sorted(data_points.items())
    ]
    
    # Top entities
    top_entities = [
        {"entity": text, "count": count}
        for text, count in entity_counter.most_common(10)
    ]
    
    return TrendAnalysisResponse(
        entity_type=params.entity_type.value if params.entity_type else "all",
        period=f"{date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}",
        data_points=trend_data,
        total_count=sum(dp.count for dp in trend_data),
        top_entities=top_entities
    )


@router.get("/entities/summary")
async def get_entity_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of all extracted entities
    """
    if not current_user.can_view_analytics:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view analytics"
        )
    
    query = db.query(
        ExtractedEntity.entity_type,
        func.count(ExtractedEntity.id).label('count')
    )
    
    if not current_user.is_admin:
        query = query.join(MedicalReport).filter(
            MedicalReport.uploaded_by == current_user.id
        )
    
    entity_counts = query.group_by(ExtractedEntity.entity_type).all()
    
    summary = {
        entity_type: count for entity_type, count in entity_counts
    }
    
    total = sum(summary.values())
    
    return {
        "total_entities": total,
        "by_type": summary
    }


@router.get("/reports/monthly")
async def get_monthly_report_stats(
    months: int = 12,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get report statistics by month for the last N months
    """
    if not current_user.can_view_analytics:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view analytics"
        )
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30 * months)
    
    query = db.query(
        func.date_trunc('month', MedicalReport.created_at).label('month'),
        func.count(MedicalReport.id).label('count')
    ).filter(
        MedicalReport.created_at >= start_date
    )
    
    if not current_user.is_admin:
        query = query.filter(MedicalReport.uploaded_by == current_user.id)
    
    monthly_stats = query.group_by('month').order_by('month').all()
    
    return {
        "months": [
            {
                "month": month.strftime("%Y-%m"),
                "count": count
            }
            for month, count in monthly_stats
        ]
    }


@router.get("/performance/ocr")
async def get_ocr_performance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get OCR performance statistics
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view performance statistics"
        )
    
    # Average confidence score
    avg_confidence = db.query(
        func.avg(MedicalReport.confidence_score)
    ).filter(
        MedicalReport.status == ReportStatus.COMPLETED
    ).scalar()
    
    # Average processing time
    avg_processing_time = db.query(
        func.avg(MedicalReport.processing_time)
    ).filter(
        MedicalReport.status == ReportStatus.COMPLETED
    ).scalar()
    
    # Success rate
    total_processed = db.query(MedicalReport).filter(
        MedicalReport.status.in_([ReportStatus.COMPLETED, ReportStatus.FAILED])
    ).count()
    
    successful = db.query(MedicalReport).filter(
        MedicalReport.status == ReportStatus.COMPLETED
    ).count()
    
    success_rate = (successful / total_processed * 100) if total_processed > 0 else 0
    
    return {
        "average_confidence": round(avg_confidence or 0, 2),
        "average_processing_time": round(avg_processing_time or 0, 2),
        "success_rate": round(success_rate, 2),
        "total_processed": total_processed,
        "successful": successful,
        "failed": total_processed - successful
    }