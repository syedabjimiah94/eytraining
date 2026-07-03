from fastapi import APIRouter
from app.services.metrics_service import MetricsService

router = APIRouter()
metrics_service = MetricsService()


@router.get("/metrics")
def get_metrics():
    return metrics_service.get_metrics()