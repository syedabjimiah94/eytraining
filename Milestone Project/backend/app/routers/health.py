from fastapi import APIRouter
from app.state.simulator_state import simulator_state
from app.state.app_state import app_state

router = APIRouter()


@router.get("/health")
def health():
    mode = "DEGRADED" if (simulator_state.api_down or simulator_state.bad_payload) else "NORMAL"
    return {
        "status": "Healthy" if mode == "NORMAL" else "Self-Healing Active",
        "service": "Weather API",
        "simulator_mode": mode,
        "total_incidents": app_state.total_incidents,
        "total_healed": app_state.total_healed,
        "last_incident": app_state.last_incident,
    }
