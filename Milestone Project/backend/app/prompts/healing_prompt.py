HEALING_PROMPT = """
You are a healing agent. Given this incident diagnosis, write a short recovery plan.
The system can retry the primary weather API, switch to mock fallback, validate schema, and create a manual investigation ticket.

Diagnosis:
{diagnosis}
"""
