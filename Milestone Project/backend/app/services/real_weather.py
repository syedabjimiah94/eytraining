import time
import requests
from app.config.settings import settings
from app.state.simulator_state import simulator_state


class RealWeather:
    """Live provider using Open-Meteo, with simulator flags for demo failures."""

    def fetch(self, city: str):
        if simulator_state.api_down:
            raise ConnectionError("Primary weather provider is unreachable")
        if simulator_state.slow_response:
            time.sleep(settings.PRIMARY_TIMEOUT_SECONDS + 1)

        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo = requests.get(
            geo_url,
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=settings.PRIMARY_TIMEOUT_SECONDS,
        )
        geo.raise_for_status()
        geo_data = geo.json()
        if not geo_data.get("results"):
            raise ValueError(f"City not found: {city}")

        place = geo_data["results"][0]
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather = requests.get(
            weather_url,
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            },
            timeout=settings.PRIMARY_TIMEOUT_SECONDS,
        )
        weather.raise_for_status()
        current = weather.json().get("current", {})
        payload = {
            "city": place.get("name", city),
            "temperature": float(current["temperature_2m"]),
            "humidity": int(current["relative_humidity_2m"]),
            "wind_speed": float(current["wind_speed_10m"]),
            "condition": self._condition_from_code(current.get("weather_code")),
            "source": "Open-Meteo Live API",
        }
        if simulator_state.bad_payload:
            payload.pop("temperature")
        return payload

    def _condition_from_code(self, code):
        mapping = {0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast", 45: "Fog", 48: "Fog", 51: "Drizzle", 61: "Rain", 63: "Rain", 65: "Heavy Rain", 71: "Snow", 80: "Rain Showers", 95: "Thunderstorm"}
        return mapping.get(int(code or 0), "Unknown")
