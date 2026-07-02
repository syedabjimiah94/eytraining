TICKET_TEMPLATE = """Manual Investigation Required

Incident ID: {incident_id}
Service: Self Healing Weather API
City: {city}
Error Type: {error_type}
Severity: {severity}

Root Cause:
{root_cause}

Original Error:
{original_error}

Retry Attempts:
{attempts}

Healing Status: {healing_status}
Healing Action: {healing_action}

Validation Status: {validation_status}
Validation Message: {validation_message}

Next Steps:
1. Check live weather provider availability and latency.
2. Verify provider response schema.
3. Check API keys, rate limits, and network path.
4. Keep fallback provider enabled until primary provider is stable.
"""
