from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/metrics")
async def metrics():
    # Placeholder for metrics collection
    return {"metrics": "metrics data"}