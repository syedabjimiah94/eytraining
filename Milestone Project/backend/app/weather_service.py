from langsmith import traceable

@traceable(name="Weather API")
def get_weather(city: str):

    weather_data = {
        "chennai": {
            "temp": "33°C",
            "condition": "Sunny",
            "humidity": "72%"
        },
        "bangalore": {
            "temp": "28°C",
            "condition": "Cloudy",
            "humidity": "65%"
        },
        "mumbai": {
            "temp": "30°C",
            "condition": "Rainy",
            "humidity": "80%"
        }
    }

    city = city.strip().lower()

    if city not in weather_data:
        return {
            "status": "FAILED",
            "message": "City not found"
        }

    return {
        "status": "SUCCESS",
        "city": city.title(),
        "temperature": weather_data[city]["temp"],
        "condition": weather_data[city]["condition"],
        "humidity": weather_data[city]["humidity"]
    }