# from fastapi import APIRouter
# from app.services.weather_service import WeatherService

# router = APIRouter()
# service = WeatherService()


# @router.get("/weather")
# def get_weather(
#     city: str,
#     mode: str | None = None,
#     failure_type: str = "success"
# ):
#     return service.get_weather(city, mode, failure_type)


# from fastapi import APIRouter, Request
# from app.services.weather_service import WeatherService

# router = APIRouter()
# service = WeatherService()


# @router.get("/weather")
# def get_weather(
#     request: Request,
#     city: str,
#     mode: str | None = None,
#     failure_type: str = "success"
# ):
#     request_id = getattr(request.state, "request_id", None)
#     return service.get_weather(city, mode, failure_type, request_id)

from fastapi import APIRouter, Request
from app.services.weather_service import WeatherService
from app.services.drift_service import DriftService

router = APIRouter()
service = WeatherService()
drift_service = DriftService()


@router.get("/weather")
def get_weather(
    request: Request,
    city: str,
    mode: str | None = None,
    failure_type: str = "success"
):
    request_id = getattr(request.state, "request_id", None)

    response = service.get_weather(city, mode, failure_type, request_id)

    if failure_type == "schema_drift":
        response.pop("humidity", None)

    if failure_type == "data_anomaly_drift":
        response["temperature"] = 999

    if "drift" not in response:
        try:
            response["drift"] = drift_service.analyze(response)
        except Exception as e:
            response["drift"] = {
                "drift_detected": False,
                "drift_type": "DRIFT_CHECK_FAILED",
                "message": str(e),
                "severity": "LOW",
            }

    return response