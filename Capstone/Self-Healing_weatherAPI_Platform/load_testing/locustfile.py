"""
Locust load test for the Self-Healing Weather API project.

Place this file at:
    C:\syed\Milestone_project\self-healing-weather-api\locustfile.py

Default behavior:
- Uses mode=mock to avoid hammering the external live weather API.
- Exercises /weather success, healable failures, drift scenarios, and observability endpoints.
- Avoids critical failures such as invalid_api_key and database_down by default.

Run examples:
    python -m locust -f locustfile.py --host http://127.0.0.1:8000
    python -m locust -f locustfile.py --headless -u 10 -r 2 -t 1m --host http://127.0.0.1:8000 --csv results\weather_load

Optional Windows env vars:
    set LOCUST_CITY=Chennai
    set LOCUST_MODE=mock
    set LOCUST_INCLUDE_FAILURES=true
    set LOCUST_INCLUDE_DRIFT=true
"""

import os
import random
from typing import Any, Dict

from locust import HttpUser, between, task


CITY = os.getenv("LOCUST_CITY", "Chennai")
MODE = os.getenv("LOCUST_MODE", "mock")  # Use mock for safe repeatable load tests.
INCLUDE_FAILURES = os.getenv("LOCUST_INCLUDE_FAILURES", "true").lower() == "true"
INCLUDE_DRIFT = os.getenv("LOCUST_INCLUDE_DRIFT", "true").lower() == "true"

# These are safe/healable in your project logic.
HEALABLE_FAILURES = [
    "network_error",
    "weather_api_down",
    "rate_limit_429",
    "invalid_json",
    "llm_timeout",
]

# These test observability/drift logic, not normal self-healing recovery.
DRIFT_FAILURES = [
    "schema_drift",
    "data_anomaly_drift",
]

# Keep these out of normal load tests because they create manual incidents/tickets.
CRITICAL_FAILURES = [
    "invalid_api_key",
    "database_down",
]


class SelfHealingWeatherUser(HttpUser):
    """Simulates users hitting your FastAPI backend directly."""

    # Real users do not click constantly. This also prevents overwhelming SQLite.
    wait_time = between(0.5, 2.0)

    def on_start(self) -> None:
        """Small startup check for each virtual user."""
        with self.client.get("/health", name="GET /health", catch_response=True) as response:
            self._expect_json(response, expected_status=200)

    def _expect_json(self, response, expected_status: int = 200) -> Dict[str, Any] | None:
        """Validate that the endpoint returned JSON and the expected HTTP status."""
        if response.status_code != expected_status:
            response.failure(f"Expected HTTP {expected_status}, got {response.status_code}")
            return None

        try:
            return response.json()
        except Exception as exc:
            response.failure(f"Response was not valid JSON: {exc}")
            return None

    def _call_weather(self, failure_type: str, name: str) -> None:
        params = {
            "city": CITY,
            "mode": MODE,
            "failure_type": failure_type,
        }

        with self.client.get(
            "/weather",
            params=params,
            name=name,
            catch_response=True,
            timeout=35,
        ) as response:
            data = self._expect_json(response, expected_status=200)
            if data is None:
                return

            # Your API returns business status inside JSON, so validate it too.
            api_status = str(data.get("status", "")).upper()
            if api_status not in {"SUCCESS", "ESCALATED"}:
                response.failure(f"Unexpected API status: {api_status}. Body: {data}")
                return

            # Basic schema checks for the main weather output.
            required_keys = ["city", "failure_type", "latency_ms", "workflow", "attempts", "request_id"]
            missing = [key for key in required_keys if key not in data]
            if missing:
                response.failure(f"Missing expected keys: {missing}")
                return

            if failure_type == "success" and api_status != "SUCCESS":
                response.failure(f"Success scenario did not return SUCCESS. Body: {data}")
                return

            if failure_type in HEALABLE_FAILURES:
                healing = data.get("healing") or {}
                if not data.get("healed") and str(healing.get("status", "")).upper() != "SUCCESS":
                    response.failure(f"Healable failure was not recovered. Body: {data}")
                    return

            if failure_type in DRIFT_FAILURES:
                drift = data.get("drift") or {}
                if not isinstance(drift, dict):
                    response.failure(f"Drift output missing or invalid. Body: {data}")
                    return

            response.success()

    @task(8)
    def weather_success(self) -> None:
        """Main healthy request path."""
        self._call_weather("success", "GET /weather success")

    @task(3)
    def weather_self_healing_failure(self) -> None:
        """Simulates failures that your project should self-heal."""
        if not INCLUDE_FAILURES:
            return
        failure_type = random.choice(HEALABLE_FAILURES)
        self._call_weather(failure_type, "GET /weather self-healing failure")

    @task(2)
    def weather_drift_scenario(self) -> None:
        """Simulates schema/data drift checks."""
        if not INCLUDE_DRIFT:
            return
        failure_type = random.choice(DRIFT_FAILURES)
        self._call_weather(failure_type, "GET /weather drift scenario")

    @task(1)
    def health_check(self) -> None:
        with self.client.get("/health", name="GET /health", catch_response=True) as response:
            self._expect_json(response, expected_status=200)

    @task(1)
    def app_metrics(self) -> None:
        with self.client.get("/metrics", name="GET /metrics", catch_response=True) as response:
            data = self._expect_json(response, expected_status=200)
            if data is not None and "requests" not in data:
                response.failure("/metrics response missing 'requests'")

    @task(1)
    def recent_request_logs(self) -> None:
        with self.client.get(
            "/request-logs",
            params={"limit": 5},
            name="GET /request-logs",
            catch_response=True,
        ) as response:
            self._expect_json(response, expected_status=200)

    @task(1)
    def recent_incidents(self) -> None:
        with self.client.get(
            "/incidents",
            params={"limit": 5},
            name="GET /incidents",
            catch_response=True,
        ) as response:
            self._expect_json(response, expected_status=200)
