from app.config.settings import settings


class TicketService:
    def send_ticket(self, subject: str, body: str) -> dict:
        if not settings.RESEND_API_KEY or not settings.INCIDENT_TO_EMAIL:
            return {
                "status": "NOT_SENT",
                "message": "Resend not configured. Set RESEND_API_KEY and INCIDENT_TO_EMAIL in .env.",
            }
        try:
            import resend
            resend.api_key = settings.RESEND_API_KEY
            result = resend.Emails.send({
                "from": settings.INCIDENT_FROM_EMAIL,
                "to": [settings.INCIDENT_TO_EMAIL],
                "subject": subject,
                "text": body,
            })
            return {"status": "SENT", "provider_response": result}
        except Exception as exc:
            return {"status": "FAILED", "message": str(exc)}
