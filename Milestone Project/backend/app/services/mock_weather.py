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

    def fetch(self, city: str):

        return {

            "city": city,

            "temperature": round(random.uniform(22, 38), 2),

            "humidity": random.randint(45, 95),

            "wind_speed": round(random.uniform(2, 18), 2),

            "condition": random.choice(self.conditions),

            "source": "Mock API"

        }