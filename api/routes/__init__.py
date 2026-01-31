"""
API Routes Package
Exports all route modules
"""

from app.api.routes import auth, upload, reports, analytics

__all__ = ["auth", "upload", "reports", "analytics"]