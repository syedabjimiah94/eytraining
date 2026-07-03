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

    healable_failures = [
        "network_error",
        "weather_api_down",
        "api_timeout",
        "rate_limit_429",
        "invalid_json",
        "llm_timeout",
    ]

    critical_failures = [
        "invalid_api_key",
        "database_down",
    ]

    if failure_type in healable_failures:
        data = recovery.recover_with_fallback(
            state["city"],
            failure_type=failure_type
        )
        data["status"] = "SUCCESS"
        data["message"] = "Primary provider failed. Self-healing returned recovered output."
        action = data.get("healing_action", "Recovered using fallback provider")

        state["healing"] = {
            "status": "SUCCESS",
            "action": action,
            "plan": plan,
        }

        state["final_response"] = data

        state["flow"].append({
            "step": "healing",
            "status": "SUCCESS",
            "message": action,
        })

    elif failure_type in critical_failures:
        action = "Automatic healing failed. Manual investigation required."

        state["healing"] = {
            "status": "ESCALATED",
            "action": action,
            "plan": plan,
        }

        state["final_response"] = {
            "city": state["city"],
            "status": "ESCALATED",
            "failure_type": failure_type,
            "message": "Critical failure detected. Email notification required.",
            "healed": False,
        }

        state["flow"].append({
            "step": "healing",
            "status": "ESCALATED",
            "message": action,
        })

    else:
        action = "No healing required"

        state["healing"] = {
            "status": "SUCCESS",
            "action": action,
            "plan": plan,
        }

        state["final_response"] = {
            "city": state["city"],
            "status": "SUCCESS",
            "failure_type": failure_type,
            "message": "Weather request completed successfully",
            "healed": False,
        }

        state["flow"].append({
            "step": "healing",
            "status": "SUCCESS",
            "message": action,
        })

    return state