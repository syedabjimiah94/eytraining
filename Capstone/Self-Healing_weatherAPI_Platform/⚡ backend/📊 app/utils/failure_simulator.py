class DemoFailure:
    SUCCESS = "success"
    NETWORK_ERROR = "network_error"
    WEATHER_API_DOWN = "weather_api_down"
    API_TIMEOUT = "api_timeout"
    RATE_LIMIT_429 = "rate_limit_429"
    INVALID_JSON = "invalid_json"
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

    if failure_type == DemoFailure.API_TIMEOUT:
        raise TimeoutError("API request timed out")

    if failure_type == DemoFailure.RATE_LIMIT_429:
        raise RuntimeError("HTTP 429 rate limit exceeded")

    if failure_type == DemoFailure.INVALID_JSON:
        raise ValueError("Invalid JSON response from weather API")

    if failure_type == DemoFailure.LLM_TIMEOUT:
        raise TimeoutError("LLM timeout")

    if failure_type == DemoFailure.INVALID_API_KEY:
        raise PermissionError("Invalid API key")

    if failure_type == DemoFailure.DATABASE_DOWN:
        raise RuntimeError("Database down")