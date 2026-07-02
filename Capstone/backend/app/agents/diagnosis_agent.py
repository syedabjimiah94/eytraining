from app.services.llm_service import LLMService
from langsmith import traceable

llm = LLMService()

@traceable(name="Diagnosis Agent")
def diagnosis_node(state):
    state.setdefault("flow", [])
    diagnosis = llm.diagnose(
        city=state.get("city", "unknown"),
        error=state.get("error", ""),
        attempts=state.get("attempts", []),
    )
    state["diagnosis"] = diagnosis
    state["flow"].append({
        "step": "diagnosis",
        "status": "SUCCESS",
        "message": f"{diagnosis.get('error_type')} - {diagnosis.get('root_cause')}",
        "llm_used": diagnosis.get("llm_used", False),
    })
    return state
