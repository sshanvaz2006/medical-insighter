"""
Analytics Service
Provides data analytics and insights
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import Counter
from app.models.report import MedicalReport, ExtractedEntity, ReportStatus


class AnalyticsService:
    """Service for generating analytics and insights"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_report_statistics(self, user_id: int = None, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive report statistics
        
        Args:
            user_id: Filter by user (None for all users)
            days: Number of days to analyze
            
        Returns:
            Dictionary with various statistics
        """
        # Date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Base query
        query = self.db.query(MedicalReport).filter(
            MedicalReport.created_at >= start_date
        )
        
        if user_id:
            query = query.filter(MedicalReport.uploaded_by == user_id)
        
        # Total reports
        total = query.count()
        
        # Status breakdown
        status_counts = {}
        for status in ReportStatus:
            count = query.filter(MedicalReport.status == status).count()
            status_counts[status.value] = count
        
        # Average processing time
        avg_processing_time = self.db.query(
            func.avg(MedicalReport.processing_time)
        ).filter(
            MedicalReport.created_at >= start_date,
            MedicalReport.status == ReportStatus.COMPLETED
        )
        
        if user_id:
            avg_processing_time = avg_processing_time.filter(
                MedicalReport.uploaded_by == user_id
            )
        
        avg_time = avg_processing_time.scalar() or 0
        
        # Average confidence
        avg_confidence = self.db.query(
            func.avg(MedicalReport.confidence_score)
        ).filter(
            MedicalReport.created_at >= start_date,
            MedicalReport.status == ReportStatus.COMPLETED
        )
        
        if user_id:
            avg_confidence = avg_confidence.filter(
                MedicalReport.uploaded_by == user_id
            )
        
        avg_conf = avg_confidence.scalar() or 0
        
        return {
            'total_reports': total,
            'status_breakdown': status_counts,
            'average_processing_time': round(avg_time, 2),
            'average_confidence': round(avg_conf, 2),
            'period_days': days
        }
    
    def get_entity_distribution(self, user_id: int = None) -> Dict[str, int]:
        """
        Get distribution of entity types
        
        Args:
            user_id: Filter by user (None for all users)
            
        Returns:
            Dictionary mapping entity types to counts
        """
        query = self.db.query(
            ExtractedEntity.entity_type,
            func.count(ExtractedEntity.id).label('count')
        )
        
        if user_id:
            query = query.join(MedicalReport).filter(
                MedicalReport.uploaded_by == user_id
            )
        
        results = query.group_by(ExtractedEntity.entity_type).all()
        
        return {entity_type: count for entity_type, count in results}
    
    def get_top_entities(
        self, 
        entity_type: str = None, 
        limit: int = 10,
        user_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get most frequent entities
        
        Args:
            entity_type: Filter by entity type
            limit: Number of top entities to return
            user_id: Filter by user
            
        Returns:
            List of entities with counts
        """
        query = self.db.query(
            ExtractedEntity.entity_text,
            ExtractedEntity.entity_type,
            func.count(ExtractedEntity.id).label('count')
        )
        
        if entity_type:
            query = query.filter(ExtractedEntity.entity_type == entity_type)
        
        if user_id:
            query = query.join(MedicalReport).filter(
                MedicalReport.uploaded_by == user_id
            )
        
        results = query.group_by(
            ExtractedEntity.entity_text,
            ExtractedEntity.entity_type
        ).order_by(func.count(ExtractedEntity.id).desc()).limit(limit).all()
        
        return [
            {
                'entity': text,
                'type': entity_type,
                'count': count
            }
            for text, entity_type, count in results
        ]
    
    def get_time_series(
        self,
        metric: str = 'reports',
        granularity: str = 'day',
        days: int = 30,
        user_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get time series data
        
        Args:
            metric: 'reports' or 'entities'
            granularity: 'day', 'week', or 'month'
            days: Number of days to analyze
            user_id: Filter by user
            
        Returns:
            List of time series data points
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        if metric == 'reports':
            query = self.db.query(
                func.date_trunc(granularity, MedicalReport.created_at).label('period'),
                func.count(MedicalReport.id).label('count')
            ).filter(
                MedicalReport.created_at >= start_date
            )
            
            if user_id:
                query = query.filter(MedicalReport.uploaded_by == user_id)
            
            results = query.group_by('period').order_by('period').all()
        
        else:  # entities
            query = self.db.query(
                func.date_trunc(granularity, MedicalReport.created_at).label('period'),
                func.count(ExtractedEntity.id).label('count')
            ).join(MedicalReport).filter(
                MedicalReport.created_at >= start_date
            )
            
            if user_id:
                query = query.filter(MedicalReport.uploaded_by == user_id)
            
            results = query.group_by('period').order_by('period').all()
        
        return [
            {
                'date': period.isoformat() if period else None,
                'count': count
            }
            for period, count in results
        ]
    
    def get_patient_insights(self, user_id: int = None) -> Dict[str, Any]:
        """
        Get insights about patients
        
        Args:
            user_id: Filter by user
            
        Returns:
            Dictionary with patient insights
        """
        query = self.db.query(MedicalReport)
        
        if user_id:
            query = query.filter(MedicalReport.uploaded_by == user_id)
        
        # Total unique patients
        total_patients = query.filter(
            MedicalReport.patient_id.isnot(None)
        ).distinct(MedicalReport.patient_id).count()
        
        # Average reports per patient
        reports_per_patient = query.filter(
            MedicalReport.patient_id.isnot(None)
        ).count() / total_patients if total_patients > 0 else 0
        
        return {
            'total_patients': total_patients,
            'average_reports_per_patient': round(reports_per_patient, 2)
        }
    
    def get_quality_metrics(self, user_id: int = None) -> Dict[str, Any]:
        """
        Get data quality metrics
        
        Args:
            user_id: Filter by user
            
        Returns:
            Dictionary with quality metrics
        """
        query = self.db.query(MedicalReport)
        
        if user_id:
            query = query.filter(MedicalReport.uploaded_by == user_id)
        
        # Completion rate
        total = query.count()
        completed = query.filter(MedicalReport.status == ReportStatus.COMPLETED).count()
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        # High confidence reports (>80%)
        high_confidence = query.filter(
            MedicalReport.confidence_score > 0.8,
            MedicalReport.status == ReportStatus.COMPLETED
        ).count()
        
        high_confidence_rate = (high_confidence / completed * 100) if completed > 0 else 0
        
        return {
            'total_reports': total,
            'completed_reports': completed,
            'completion_rate': round(completion_rate, 2),
            'high_confidence_reports': high_confidence,
            'high_confidence_rate': round(high_confidence_rate, 2)
        }