import time
from fastapi import HTTPException
import random

class MockWeather:

    conditions = [
        "Sunny",
        "Cloudy",
        "Rainy",
        "Storm",
        "Fog",
        "Windy"
    ]

    def simulate_failure(self, scenario: str):

        if scenario == "success":
            return

        elif scenario == "network_error":
            raise HTTPException(status_code=503, detail="Simulated network failure")

        elif scenario == "weather_api_down":
            raise HTTPException(status_code=503, detail="Weather API unavailable")

        elif scenario == "api_timeout":
            time.sleep(10)
            raise HTTPException(status_code=504, detail="API timeout")

        elif scenario == "rate_limit_429":
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        elif scenario == "invalid_json":
            return {
                "city": None,
                "temperature": "invalid",
                "condition": None
            }

        elif scenario == "llm_timeout":
            raise HTTPException(status_code=504, detail="LLM timeout")

        elif scenario == "invalid_api_key":
            raise HTTPException(status_code=401, detail="Invalid API key")

        elif scenario == "database_down":
            raise HTTPException(status_code=500, detail="Database unavailable")

        elif scenario == "docker_crash":
            raise HTTPException(status_code=500, detail="Container crashed")

        elif scenario == "high_cpu":
            raise HTTPException(status_code=503, detail="High CPU usage")

        elif scenario == "memory_leak":
            raise HTTPException(status_code=503, detail="Memory leak detected")

    def fetch(self, city: str):

        return {
            "city": city,
            "temperature": round(random.uniform(22, 38), 2),
            "humidity": random.randint(45, 95),
            "wind_speed": round(random.uniform(2, 18), 2),
            "condition": random.choice(self.conditions),
            "source": "Mock API"
        }