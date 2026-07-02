from app.services.recovery_service import RecoveryService
from app.services.llm_service import LLMService
from langsmith import traceable

recovery = RecoveryService()
llm = LLMService()

@traceable(name="Healing Agent")
def healing_node(state):
    state.setdefault("flow", [])

    failure_type = state.get("failure_type", "success")
    plan = llm.healing_plan(state.get("diagnosis", {}))

    if failure_type in ["network_error", "weather_api_down", "llm_timeout"]:
        data = recovery.recover_with_fallback(state["city"])

        if failure_type == "network_error":
            action = "Retry completed and service recovered"

        elif failure_type == "weather_api_down":
            action = "Weather API failed, switched to fallback cache"

        elif failure_type == "llm_timeout":
            action = "LLM timeout detected, switched to backup recovery plan"

        data["healed"] = True
        data["healing_action"] = action

        state["final_response"] = data
        state["healing"] = {
            "status": "SUCCESS",
            "action": action,
            "plan": plan
        }

        state["flow"].append({
            "step": "healing",
            "status": "SUCCESS",
            "message": action,
            "llm_used": plan.get("llm_used", False)
        })

        return state

    if failure_type in ["invalid_api_key", "database_down"]:
        action = "Automatic healing failed. Manual investigation required."

        state["healing"] = {
            "status": "FAILED",
            "action": action,
            "plan": plan
        }

        state["flow"].append({
            "step": "healing",
            "status": "FAILED",
            "message": action
        })

        return state

    state["healing"] = {
        "status": "NOT_REQUIRED",
        "action": "No healing required"
    }

    return state