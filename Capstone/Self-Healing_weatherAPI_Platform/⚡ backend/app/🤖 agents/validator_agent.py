from app.services.monitoring_service import MonitoringService
from langsmith import traceable

monitoring = MonitoringService()

@traceable(name="Validation Agent")
def validator_node(state):
    state.setdefault("flow", [])

    healing = state.get("healing", {})

    if healing.get("status") == "FAILED":
        state["verification"] = {
            "status": "FAILED",
            "message": "Validation failed because healing failed"
        }

        state["flow"].append({
            "step": "validate",
            "status": "FAILED",
            "message": "Validation failed. Sending to manual investigation."
        })

        return state

    try:
        monitoring.validate_weather_payload(state["final_response"])

        state["verification"] = {
            "status": "SUCCESS",
            "message": "Recovered response schema is valid"
        }

        state["flow"].append({
            "step": "validate",
            "status": "SUCCESS",
            "message": "Recovered response is valid"
        })

    except Exception as exc:
        state["verification"] = {
            "status": "FAILED",
            "message": str(exc)
        }

        state["flow"].append({
            "step": "validate",
            "status": "FAILED",
            "message": str(exc)
        })

    return state