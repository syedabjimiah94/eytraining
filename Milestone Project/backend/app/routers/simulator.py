from fastapi import APIRouter
from app.state.simulator_state import simulator_state

router = APIRouter(prefix="/simulator", tags=["Simulator"])


@router.get("/status")
def simulator_status():
    return {
        "api_down": simulator_state.api_down,
        "slow_response": simulator_state.slow_response,
        "bad_payload": simulator_state.bad_payload,
    }


@router.post("/api-down/{enabled}")
def set_api_down(enabled: bool):
    simulator_state.api_down = enabled
    return simulator_status()


@router.post("/slow-response/{enabled}")
def set_slow_response(enabled: bool):
    simulator_state.slow_response = enabled
    return simulator_status()


@router.post("/bad-payload/{enabled}")
def set_bad_payload(enabled: bool):
    simulator_state.bad_payload = enabled
    return simulator_status()


@router.post("/reset")
def reset_simulator():
    simulator_state.api_down = False
    simulator_state.slow_response = False
    simulator_state.bad_payload = False
    return simulator_status()
