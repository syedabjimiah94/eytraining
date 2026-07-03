from app.services.mock_weather import MockWeather


class RecoveryService:
    def __init__(self):
        self.fallback = MockWeather()

    RECOVERY_ACTIONS = {
        "network_error": "Retry request after reconnecting network",
        "weather_api_down": "Switched traffic to mock fallback provider",
        "api_timeout": "Retry request with exponential backoff",
        "rate_limit_429": "Backoff and retry after delay",
        "invalid_json": "Validate response and retry API",
        "llm_timeout": "Use rule-based fallback diagnosis",
        "invalid_api_key": "Escalate to administrator",
        "database_down": "Store temporarily and retry database connection",
        "docker_crash": "Restart container",
        "high_cpu": "Scale container / reduce workload",
        "memory_leak": "Restart application process",
    }

    def recover_with_fallback(self, city: str, failure_type: str = "weather_api_down"):
        data = self.fallback.fetch(city)
        data["healed"] = True
        data["failure_type"] = failure_type
        data["healing_action"] = self.RECOVERY_ACTIONS.get(
            failure_type,
            "Fallback recovery executed"
        )
        return data