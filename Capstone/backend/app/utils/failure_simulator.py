class DemoFailure:
    SUCCESS = "success"
    NETWORK_ERROR = "network_error"
    WEATHER_API_DOWN = "weather_api_down"
    LLM_TIMEOUT = "llm_timeout"
    INVALID_API_KEY = "invalid_api_key"
    DATABASE_DOWN = "database_down"


def simulate_failure(failure_type: str):
    if failure_type == DemoFailure.SUCCESS:
        return

    if failure_type == DemoFailure.NETWORK_ERROR:
        raise ConnectionError("Temporary network error")

    if failure_type == DemoFailure.WEATHER_API_DOWN:
        raise ConnectionError("Weather API is down")

    if failure_type == DemoFailure.LLM_TIMEOUT:
        raise TimeoutError("LLM timeout")

    if failure_type == DemoFailure.INVALID_API_KEY:
        raise PermissionError("Invalid API key")

    if failure_type == DemoFailure.DATABASE_DOWN:
        raise RuntimeError("Database down")