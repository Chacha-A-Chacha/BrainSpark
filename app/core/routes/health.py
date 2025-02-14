# app/routes/health.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.dependencies import get_voter_hash

router = APIRouter(tags=["System Health"])

@router.get("/health", summary="System Health Check")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check endpoint verifying:
    - Database connectivity
    - Core service availability
    """
    try:
        # Check database connection
        await db.execute(text("SELECT 1"))
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "services": {
                    "database": "operational",
                    "api": "operational"
                },
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": "Database connection failed",
                "services": {
                    "database": "unavailable",
                    "api": "degraded"
                }
            }
        )

@router.get("/settings", include_in_schema=False)
async def show_settings():
    """Display non-sensitive configuration values (for debugging)"""
    return {
        "environment": settings.ENVIRONMENT,
        "debug_mode": settings.DEBUG,
        "database": str(settings.DATABASE_URL).split("@")[-1],
        "prometheus_enabled": settings.ENABLE_PROMETHEUS,
        "rate_limiting": {
            "submissions": settings.SUBMISSION_RATE_LIMIT,
            "voting": settings.VOTING_RATE_LIMIT
        }
    }

@router.get("/readyz", tags=["System Health"])
async def readiness_probe():
    """Kubernetes-style readiness probe"""
    return PlainTextResponse("OK")

@router.get("/livez", tags=["System Health"])
async def liveness_probe():
    """Kubernetes-style liveness probe"""
    return PlainTextResponse("OK")
