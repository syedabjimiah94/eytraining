# from app.services.llm_service import LLMService
# from langsmith import traceable

# llm = LLMService()

# @traceable(name="Diagnosis Agent")
# def diagnosis_node(state):
#     state.setdefault("flow", [])
#     diagnosis = llm.diagnose(
#         city=state.get("city", "unknown"),
#         error=state.get("error", ""),
#         attempts=state.get("attempts", []),
#     )
#     state["diagnosis"] = diagnosis
#     state["flow"].append({
#         "step": "diagnosis",
#         "status": "SUCCESS",
#         "message": f"{diagnosis.get('error_type')} - {diagnosis.get('root_cause')}",
#         "llm_used": diagnosis.get("llm_used", False),
#     })
#     return state


from app.services.llm_service import LLMService
from langsmith import traceable

llm = LLMService()

FAILURE_DIAGNOSIS_MAP = {
    "network_error": "Network connection failed or service unreachable",
    "weather_api_down": "External weather API is unavailable",
    "api_timeout": "Weather API request timed out",
    "rate_limit_429": "Weather API rate limit exceeded",
    "invalid_json": "Weather API returned invalid response format",
    "llm_timeout": "LLM response timed out",
    "invalid_api_key": "Weather API key is invalid or expired",
    "database_down": "Database connection failed",
}


@traceable(name="Diagnosis Agent")
def diagnosis_node(state):
    state.setdefault("flow", [])

    failure_type = state.get("failure_type", "success")

    diagnosis = llm.diagnose(
        city=state.get("city", "unknown"),
        error=state.get("error", failure_type),
        attempts=state.get("attempts", []),
    )

    if failure_type != "success":
        diagnosis["error_type"] = failure_type
        diagnosis["root_cause"] = FAILURE_DIAGNOSIS_MAP.get(
            failure_type,
            diagnosis.get("root_cause", "Unknown failure detected")
        )

    state["diagnosis"] = diagnosis

    state["flow"].append({
        "step": "diagnosis",
        "status": "SUCCESS",
        "message": f"{diagnosis.get('error_type')} - {diagnosis.get('root_cause')}",
        "llm_used": diagnosis.get("llm_used", False),
    })

    return state