import time
from datetime import datetime

from app.agents.graph import run_self_healing_workflow
from app.database.database import save_request_log
from app.services.drift_service import DriftService
from app.services.metrics_service import MetricsService
from app.services.prometheus_metrics import record_weather_observability
from app.services.recovery_service import RecoveryService

metrics_service = MetricsService()
drift_service = DriftService()
recovery_service = RecoveryService()


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
            "message": "Manual investigation required",
        }

        # Important demo fix:
        # If mode=live and failure_type=success, but the live provider/gateway is unreachable,
        # the monitoring agent receives a real HTTP/provider error. Older healing logic may not
        # classify this as a healable simulated failure because failure_type is still "success".
        # This block converts that real runtime provider error into live_provider_unreachable
        # and returns fallback weather, so the backend response clearly shows self-healing.
        actual_error = state.get("error")
        actual_mode = state.get("mode") or mode
        if actual_error and actual_mode == "live" and failure_type == "success":
            fallback = recovery_service.recover_with_fallback(
                city,
                failure_type="live_provider_unreachable",
            )
            fallback["status"] = "HEALED"
            fallback["message"] = "Live Open-Meteo provider was unreachable. Self-healing returned fallback weather output."
            fallback["recovery_action"] = "Switched to fallback mock provider"
            fallback["live_provider_error"] = actual_error
            fallback["source"] = fallback.get("source", "Mock API")

            response = fallback

            state["diagnosis"] = state.get("diagnosis") or {
                "error_type": "LIVE_PROVIDER_UNREACHABLE",
                "severity": "HIGH",
                "root_cause": "Open-Meteo gateway/provider returned an unreachable error during a live request.",
            }
            state["healing"] = state.get("healing") or {
                "status": "HEALED",
                "action": "Switched to fallback mock provider",
            }
            if state.get("healing", {}).get("action") == "No healing required":
                state["healing"] = {
                    "status": "HEALED",
                    "action": "Switched to fallback mock provider",
                    "reason": "Live provider failed even though failure_type was success.",
                }

            state.setdefault("flow", []).append({
                "step": "live_provider_unreachable",
                "status": "FAILED",
                "message": f"Live provider/gateway was unreachable: {actual_error}",
            })
            state.setdefault("flow", []).append({
                "step": "service_level_healing",
                "status": "SUCCESS",
                "message": "WeatherService returned fallback weather after live provider failure.",
            })

        response["latency_ms"] = latency_ms
        response["workflow"] = state.get("flow", [])
        response["attempts"] = state.get("attempts", [])
        response["mode"] = state.get("mode") or mode
        response["failure_type"] = response.get("failure_type", failure_type)
        response["requested_failure_type"] = failure_type
        response["diagnosis"] = state.get("diagnosis")
        response["healing"] = state.get("healing")
        response["verification"] = state.get("verification")
        response["ticket"] = state.get("ticket")
        response["incident_id"] = state.get("incident_id")
        response["incident_storage"] = state.get("incident_storage")
        response["notification"] = state.get("notification")
        response["request_id"] = request_id

        if response.get("failure_type") == "live_provider_unreachable":
            response["healed"] = True
            response["provider_status"] = "unreachable"
            response["self_healing_summary"] = {
                "failure": "Live provider unreachable",
                "detected_by": "Monitoring Agent / WeatherService",
                "recovery_action": "Fallback mock provider used",
                "validated": bool(state.get("verification")),
                "incident_logged": bool(state.get("incident_id")),
                "incident_saved_to": (state.get("incident_storage") or {}).get("saved_to"),
            }

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
                "mode": state.get("mode") or mode,
                "failure_type": response.get("failure_type", failure_type),
                "final_status": response.get("status", "UNKNOWN"),
                "error_type": (
                    drift.get("drift_type")
                    if drift.get("drift_detected")
                    else diagnosis.get("error_type")
                ) if isinstance(diagnosis, dict) else response.get("failure_type", failure_type),
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
                        or response.get("recovery_action")
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
