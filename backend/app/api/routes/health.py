"""Health check routes"""

from fastapi import APIRouter
from datetime import datetime
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/db")
async def health_check_database():
    """Database health check endpoint"""
    # TODO: Implement actual database check
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }

