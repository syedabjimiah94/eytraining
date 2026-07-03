HEALING_PROMPT = """
You are a healing agent for a self-healing weather API.

Available recovery actions:
- Retry primary weather API
- Switch to mock fallback provider
- Apply timeout/backoff handling
- Validate response schema
- Use rule-based fallback when LLM fails
- Escalate invalid API key or database outage by creating manual investigation ticket

Given this incident diagnosis, write a short recovery plan.

Diagnosis:
{diagnosis}
"""