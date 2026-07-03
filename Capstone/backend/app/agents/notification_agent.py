from datetime import datetime
from app.database.database import save_incident, update_ticket
from app.services.llm_service import LLMService
from app.services.ticket_service import TicketService
from app.state.app_state import app_state
from langsmith import traceable

llm = LLMService()
tickets = TicketService()

@traceable(name="Notification Agent")
def notification_node(state):
    state.setdefault("flow", [])
    diagnosis = state.get("diagnosis", {})
    healing = state.get("healing", {})
    verification = state.get("verification", {})
    # needs_manual = healing.get("status") != "SUCCESS" or verification.get("status") != "SUCCESS"
    failure_type = state.get("failure_type", "success")

    CRITICAL_FAILURES = [
        "invalid_api_key",
        "database_down",
    ]

    needs_manual = failure_type in CRITICAL_FAILURES

    incident = {
        "city": state.get("city", "unknown"),
        "error_type": diagnosis.get("error_type", "UNKNOWN"),
        "severity": diagnosis.get("severity", "MEDIUM"),
        "message": state.get("error", "No error"),
        "status": "MANUAL_INVESTIGATION_REQUIRED" if needs_manual else healing.get("status", "NOT_REQUIRED"),
        "action_taken": healing.get("action", "No action"),
        "diagnosis": diagnosis,
        "attempts": state.get("attempts", []),
        "flow": state.get("flow", []),
        "ticket_status": "NOT_REQUIRED",
        "ticket_body": "",
        "created_at": datetime.utcnow().isoformat(),
    }

    incident_id = save_incident(incident)
    state["incident_id"] = incident_id

    ticket = {"status": "NOT_REQUIRED"}
    if needs_manual:
        state["incident_id"] = incident_id
        body = llm.ticket_body(state)
        ticket = tickets.send_ticket(
            subject=f"🚨 Manual Investigation Required: Weather API incident #{incident_id}",
            body=body,
        )
        ticket["body"] = body
        update_ticket(incident_id, ticket.get("status", "UNKNOWN"), body)
        state["flow"].append({"step": "ticket", "status": ticket.get("status"), "message": "Manual investigation ticket created"})

    incident["id"] = incident_id
    incident["ticket_status"] = ticket.get("status")
    app_state.last_incident = incident
    app_state.total_incidents += 1
    # if healing.get("status") == "SUCCESS" and verification.get("status") == "SUCCESS":
    if healing.get("status") in ["SUCCESS", "HEALED"] and verification.get("status") == "SUCCESS":
        app_state.total_healed += 1

    state["ticket"] = ticket
    state["notification"] = {"status": "SAVED", "incident": incident}
    state["flow"].append({"step": "notification", "status": "SAVED", "message": f"Incident saved in SQLite with ID {incident_id}"})
    return state
