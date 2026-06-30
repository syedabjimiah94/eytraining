from app.services.mock_weather import MockWeather


class RecoveryService:
    def __init__(self):
        self.fallback = MockWeather()

    def recover_with_fallback(self, city: str):
        data = self.fallback.fetch(city)
        data["healed"] = True
        data["healing_action"] = "Switched traffic to mock fallback provider"
        return data
