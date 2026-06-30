import json
from app.config.settings import settings
from langchain_openai import ChatOpenAI

def _fallback_diagnosis(error: str, attempts: list[dict]):
    lowered = error.lower()
    if "timeout" in lowered or "timed out" in lowered:
        error_type = "TIMEOUT"
        root_cause = "Primary weather provider did not respond within timeout."
        severity = "HIGH"
    elif "schema" in lowered or "missing" in lowered or "payload" in lowered:
        error_type = "BAD_PAYLOAD"
        root_cause = "Provider response did not match the expected weather schema."
        severity = "MEDIUM"
    elif "unreachable" in lowered or "connection" in lowered or "provider" in lowered:
        error_type = "PROVIDER_DOWN"
        root_cause = "Primary weather provider is unreachable after retries."
        severity = "HIGH"
    else:
        error_type = "UNKNOWN"
        root_cause = "Unexpected failure in primary weather pipeline."
        severity = "MEDIUM"
    return {
        "error_type": error_type,
        "severity": severity,
        "root_cause": root_cause,
        "llm_used": False,
        "attempt_count": len(attempts),
        "recommendation": "Use fallback weather provider and create manual investigation ticket if validation fails.",
    }




class LLMService:

    def __init__(self):
        self.llm = None

        if settings.OPENAI_API_KEY:
            from langchain_openai import ChatOpenAI

            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0
            )

    def enabled(self):
        return self.llm is not None

    def diagnose(self, city: str, error: str, attempts: list[dict]):
        if not self.enabled():
            return _fallback_diagnosis(error, attempts)

        try:
            from app.prompts.diagnosis_prompt import DIAGNOSIS_PROMPT

            prompt = DIAGNOSIS_PROMPT.format(
                city=city,
                error=error,
                attempts=json.dumps(attempts, indent=2)
            )

            result = self.llm.invoke(prompt).content
            data = json.loads(result)
            data["llm_used"] = True
            data["attempt_count"] = len(attempts)
            return data

        except Exception as exc:
            data = _fallback_diagnosis(error, attempts)
            data["llm_error"] = str(exc)
            return data

    def healing_plan(self, diagnosis: dict):
        if not self.enabled():
            return {
                "llm_used": False,
                "plan": "Route traffic to fallback mock provider, validate schema, and create ticket if recovery fails.",
            }

        try:
            from app.prompts.healing_prompt import HEALING_PROMPT

            prompt = HEALING_PROMPT.format(
                diagnosis=json.dumps(diagnosis, indent=2)
            )

            result = self.llm.invoke(prompt).content

            return {
                "llm_used": True,
                "plan": result
            }

        except Exception as exc:
            return {
                "llm_used": False,
                "plan": "Fallback to mock provider.",
                "llm_error": str(exc)
            }

            
    def ticket_body(self, state: dict):
        from app.prompts.notification_prompt import TICKET_TEMPLATE
        diagnosis = state.get("diagnosis", {})
        healing = state.get("healing", {})
        verification = state.get("verification", {})
        return TICKET_TEMPLATE.format(
            city=state.get("city"),
            error_type=diagnosis.get("error_type"),
            severity=diagnosis.get("severity"),
            root_cause=diagnosis.get("root_cause"),
            original_error=state.get("error"),
            attempts=json.dumps(state.get("attempts", []), indent=2),
            healing_status=healing.get("status"),
            healing_action=healing.get("action"),
            validation_status=verification.get("status"),
            validation_message=verification.get("message"),
            incident_id=state.get("incident_id", "pending"),
        )
