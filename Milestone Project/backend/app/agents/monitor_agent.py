import time

from app.config.settings import settings
from app.services.real_weather import RealWeather
from app.services.mock_weather import MockWeather
from app.services.monitoring_service import MonitoringService
from app.utils.failure_simulator import simulate_failure
from langsmith import traceable

provider = RealWeather()
mock_provider = MockWeather()
monitoring = MonitoringService()

@traceable(name="Monitoring Agent")
def monitoring_node(state):
    state.setdefault("flow", [])
    state["attempts"] = []

    city = state["city"]
    mode = state.get("mode") or settings.WEATHER_PROVIDER_MODE
    failure_type = state.get("failure_type", "success")

    state["mode"] = mode

    last_error = None

    for attempt_no in range(1, settings.PRIMARY_RETRY_COUNT + 1):
        try:
            simulate_failure(failure_type)

            if mode == "mock":
                data = mock_provider.fetch(city)
            else:
                data = provider.fetch(city)

            monitoring.validate_weather_payload(data)

            state["primary_response"] = data
            state["final_response"] = data
            state["error"] = ""

            state["attempts"].append({
                "attempt": attempt_no,
                "status": "SUCCESS"
            })

            state["flow"].append({
                "step": "monitor",
                "status": "SUCCESS",
                "message": f"Weather request succeeded on attempt {attempt_no}"
            })

            return state

        except Exception as exc:
            last_error = str(exc)

            state["attempts"].append({
                "attempt": attempt_no,
                "status": "FAILED",
                "error": last_error
            })

            state["flow"].append({
                "step": "monitor",
                "status": "FAILED",
                "message": f"Attempt {attempt_no} failed: {last_error}"
            })

            if attempt_no < settings.PRIMARY_RETRY_COUNT:
                time.sleep(settings.PRIMARY_RETRY_DELAY_SECONDS)

    state["error"] = last_error or "Unknown weather provider error"

    state["monitoring"] = {
        "status": "FAILED",
        "error": state["error"]
    }

    state["flow"].append({
        "step": "monitor",
        "status": "FAILED",
        "message": f"Primary provider failed after {settings.PRIMARY_RETRY_COUNT} retries"
    })

    return state