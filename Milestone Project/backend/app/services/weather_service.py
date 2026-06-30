from app.agents.graph import run_self_healing_workflow
import time

class WeatherService:
    def get_weather(
        self,
        city: str,
        mode: str | None = None,
        failure_type: str = "success"
    ):
        start = time.perf_counter()
        state = run_self_healing_workflow(city, mode, failure_type)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        response = state.get("final_response", {
            "city": city,
            "status": "FAILED",
            "message": "Manual investigation required"
        })
        response["latency_ms"] = latency_ms
        response["workflow"] = state.get("flow", [])
        response["attempts"] = state.get("attempts", [])
        response["mode"] = state.get("mode")
        response["failure_type"] = failure_type
        response["diagnosis"] = state.get("diagnosis")
        response["healing"] = state.get("healing")
        response["verification"] = state.get("verification")
        response["ticket"] = state.get("ticket")
        response["incident_id"] = state.get("incident_id")

        return response