# from fastapi import APIRouter
# from app.services.metrics_service import MetricsService

# router = APIRouter()
# metrics_service = MetricsService()


# @router.get("/metrics")
# def get_metrics():
#     return metrics_service.get_metrics()



# from fastapi import Response
# from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# @router.get("/prometheus-metrics")
# def prometheus_metrics():
#     return Response(
#         content=generate_latest(),
#         media_type=CONTENT_TYPE_LATEST
#     )
from fastapi import APIRouter, Response
from app.services.metrics_service import MetricsService
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter()
metrics_service = MetricsService()


@router.get("/metrics")
def get_metrics():
    # Existing JSON metrics used by your application/dashboard.
    return metrics_service.get_metrics()


@router.get("/prometheus-metrics")
def prometheus_metrics():
    # Prometheus-compatible metrics endpoint.
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
