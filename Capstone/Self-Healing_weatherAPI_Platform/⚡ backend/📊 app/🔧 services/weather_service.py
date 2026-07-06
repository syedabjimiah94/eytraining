# from app.agents.graph import run_self_healing_workflow
# import time
# from app.services.metrics_service import MetricsService

# metrics_service = MetricsService()
# class WeatherService:
#     def get_weather(
#         self,
#         city: str,
#         mode: str | None = None,
#         failure_type: str = "success"
#     ):
#         start = time.perf_counter()
#         state = run_self_healing_workflow(city, mode, failure_type)
#         latency_ms = round((time.perf_counter() - start) * 1000, 2)

#         response = state.get("final_response", {
#             "city": city,
#             "status": "FAILED",
#             "message": "Manual investigation required"
#         })
#         response["latency_ms"] = latency_ms
#         response["workflow"] = state.get("flow", [])
#         response["attempts"] = state.get("attempts", [])
#         response["mode"] = state.get("mode")
#         response["failure_type"] = failure_type
#         response["diagnosis"] = state.get("diagnosis")
#         response["healing"] = state.get("healing")
#         response["verification"] = state.get("verification")
#         response["ticket"] = state.get("ticket")
#         response["incident_id"] = state.get("incident_id")
#         metrics_service.record(response)

#         return response



from app.agents.graph import run_self_healing_workflow
import time
from datetime import datetime
from app.services.metrics_service import MetricsService
from app.database.database import save_request_log
from app.services.drift_service import DriftService
from app.services.prometheus_metrics import record_weather_observability

metrics_service = MetricsService()
drift_service = DriftService()

class WeatherService:
    def get_weather(
        self,
        city: str,
        mode: str | None = None,
        failure_type: str = "success",
        request_id: str | None = None,
    ):
        start = time.perf_counter()
        state = run_self_healing_workflow(city, mode, failure_type)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        response = state.get("final_response") or {
            "city": city,
            "status": "FAILED",
            "message": "Manual investigation required"
        }

        response["latency_ms"] = latency_ms
        response["workflow"] = state.get("flow", [])
        response["attempts"] = state.get("attempts", [])
        response["mode"] = state.get("mode")
        response["failure_type"] = failure_type
        response["diagnosis"] = state.get("diagnosis")
        response["healing"] = state.get("healing")
        response["verification"] = state.get("verification")
        response["ticket"] = state.get("ticket")
        response["incident_id"] = state.get("incident_id")
        response["request_id"] = request_id

        if failure_type == "schema_drift":
            response.pop("humidity", None)

        if failure_type == "data_anomaly_drift":
            response["temperature"] = 999

        try:
            response["drift"] = drift_service.analyze(response)
        except Exception as e:
            response["drift"] = {
                "drift_detected": False,
                "drift_type": "DRIFT_CHECK_FAILED",
                "message": str(e),
                "severity": "LOW",
            }

        diagnosis = state.get("diagnosis") or {}
        healing = state.get("healing") or {}
        verification = state.get("verification") or {}
        drift = response.get("drift", {})

        try:
            request_log_id = save_request_log({
                "request_id": request_id,
                "city": city,
                "mode": state.get("mode"),
                "failure_type": failure_type,
                "final_status": response.get("status", "UNKNOWN"),

                "error_type": (
                    drift.get("drift_type")
                    if drift.get("drift_detected")
                    else diagnosis.get("error_type")
                ) if isinstance(diagnosis, dict) else failure_type,

                "diagnosis": (
                    drift.get("message")
                    if drift.get("drift_detected")
                    else (
                        diagnosis.get("root_cause")
                        or diagnosis.get("summary")
                        or str(diagnosis)
                    )
                ) if isinstance(diagnosis, dict) else str(diagnosis),

                "healing_action": (
                    "No healing required - drift logged for observability"
                    if drift.get("drift_detected")
                    else (
                        healing.get("action")
                        or healing.get("strategy")
                        or str(healing)
                    )
                ) if isinstance(healing, dict) else str(healing),

                "validation_result": (
                    verification.get("status")
                    or verification.get("message")
                    or str(verification)
                ) if isinstance(verification, dict) else str(verification),

                "incident_id": state.get("incident_id"),
                "latency_ms": latency_ms,
                "created_at": datetime.utcnow().isoformat(),
            })

            response["request_log_id"] = request_log_id
            print(f"✅ Request log saved: {request_log_id}")

        except Exception as e:
            print(f"❌ Failed to save request log: {e}")
            response["request_log_error"] = str(e)

        metrics_service.record(response)
        record_weather_observability(response)

        return response