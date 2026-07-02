from app.models.weather import WeatherResponse


class MonitoringService:
    required_fields = set(WeatherResponse.model_fields.keys())

    def validate_weather_payload(self, payload: dict):
        missing = self.required_fields - set(payload.keys())
        if missing:
            raise ValueError(f"Weather payload missing fields: {', '.join(sorted(missing))}")
        return True
