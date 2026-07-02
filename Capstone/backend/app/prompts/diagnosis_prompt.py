DIAGNOSIS_PROMPT = """
You are an SRE diagnosis agent for a self-healing weather API.
Return ONLY valid JSON with these keys:
error_type, severity, root_cause, recommendation.

City: {city}
Final error: {error}
Retry attempts: {attempts}
"""
