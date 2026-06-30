class SimulatorState:
    """In-memory switches used to simulate production failures."""

    api_down: bool = False
    slow_response: bool = False
    bad_payload: bool = False


simulator_state = SimulatorState()
