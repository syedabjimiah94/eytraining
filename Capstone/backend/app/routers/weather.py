from fastapi import APIRouter
from app.services.weather_service import WeatherService

router = APIRouter()
service = WeatherService()


@router.get("/weather")
def get_weather(
    city: str,
    mode: str | None = None,
    failure_type: str = "success"
):
    return service.get_weather(city, mode, failure_type)