from prometheus_client import Counter, Histogram


def _label(value, default="unknown"):
    if value is None or value == "":
        return default
    return str(value).replace(" ", "_").lower()[:80]


WEATHER_REQUESTS_TOTAL = Counter(
    "weather_requests_total",
    "Total weather requests handled by the application",
    ["mode", "failure_type", "status"],
)

WEATHER_REQUEST_LATENCY_SECONDS = Histogram(
    "weather_request_latency_seconds",
    "Weather request latency in seconds",
    ["failure_type"],
)

SELF_HEALING_AGENT_STEPS_TOTAL = Counter(
    "self_healing_agent_steps_total",
    "Total self-healing workflow agent steps",
    ["agent", "status"],
)

SELF_HEALING_ATTEMPTS_TOTAL = Counter(
    "self_healing_primary_attempts_total",
    "Primary weather provider attempts",
    ["status"],
)

SELF_HEALING_ACTIONS_TOTAL = Counter(
    "self_healing_actions_total",
    "Healing actions executed by the application",
    ["failure_type", "status"],
)

SELF_HEALING_INCIDENTS_TOTAL = Counter(
    "self_healing_incidents_total",
    "Incidents created by the self-healing workflow",
    ["failure_type", "error_type", "status"],
)

WEATHER_DRIFT_EVENTS_TOTAL = Counter(
    "weather_drift_events_total",
    "Weather data drift events detected",
    ["drift_type", "severity"],
)


def record_weather_observability(response: dict) -> None:
    """Record project-specific Prometheus metrics from one weather API response.

    This function is safe: it never raises an exception back to the application.
    """
    try:
        failure_type = _label(response.get("failure_type"), "success")
        mode = _label(response.get("mode"), "default")
        status = _label(response.get("status"), "unknown")

        WEATHER_REQUESTS_TOTAL.labels(
            mode=mode,
            failure_type=failure_type,
            status=status,
        ).inc()

        latency_ms = response.get("latency_ms")
        if isinstance(latency_ms, (int, float)):
            WEATHER_REQUEST_LATENCY_SECONDS.labels(
                failure_type=failure_type
            ).observe(latency_ms / 1000)

        for attempt in response.get("attempts") or []:
            SELF_HEALING_ATTEMPTS_TOTAL.labels(
                status=_label(attempt.get("status"))
            ).inc()

        for step in response.get("workflow") or []:
            SELF_HEALING_AGENT_STEPS_TOTAL.labels(
                agent=_label(step.get("step")),
                status=_label(step.get("status")),
            ).inc()

        healing = response.get("healing") or {}
        if healing:
            SELF_HEALING_ACTIONS_TOTAL.labels(
                failure_type=failure_type,
                status=_label(healing.get("status")),
            ).inc()

        diagnosis = response.get("diagnosis") or {}
        if response.get("incident_id"):
            SELF_HEALING_INCIDENTS_TOTAL.labels(
                failure_type=failure_type,
                error_type=_label(diagnosis.get("error_type")),
                status=status,
            ).inc()

        drift = response.get("drift") or {}
        if drift.get("drift_detected"):
            WEATHER_DRIFT_EVENTS_TOTAL.labels(
                drift_type=_label(drift.get("drift_type")),
                severity=_label(drift.get("severity")),
            ).inc()

    except Exception:
        # Prometheus recording must never break the business flow.
        return
