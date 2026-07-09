from datetime import datetime
from app.database.database import save_incident, update_ticket
from app.services.llm_service import LLMService
from app.services.ticket_service import TicketService
from app.state.app_state import app_state
from app.state.simulator_state import simulator_state
from langsmith import traceable

llm = LLMService()
tickets = TicketService()


def _normalise_storage_result(raw_result):
    """Return a consistent incident_storage JSON object for UI/backend response.

    This function supports both database implementations:
    1. save_incident() returns only an integer incident_id.
    2. save_incident() returns a dict with incident_id + db_failover details.
    """
    if isinstance(raw_result, dict):
        incident_id = raw_result.get("incident_id")
        storage = {
            "incident_id": incident_id,
            "db_failover": bool(raw_result.get("db_failover", False)),
            "primary_db": raw_result.get("primary_db", "failed" if raw_result.get("db_failover") else "used"),
            "secondary_db": raw_result.get("secondary_db", "used" if raw_result.get("db_failover") else "not_used"),
            "saved_to": raw_result.get("saved_to", "secondary_incidents.db" if raw_result.get("db_failover") else "incidents.db"),
            "message": raw_result.get("message", "Incident storage completed"),
        }
        if raw_result.get("primary_error"):
            storage["primary_error"] = raw_result.get("primary_error")
        return incident_id, storage

    # Backward-compatible path: older save_incident() returns only an int.
    incident_id = raw_result
    if getattr(simulator_state, "database_down", False):
        storage = {
            "incident_id": incident_id,
            "db_failover": True,
            "primary_db": "failed",
            "secondary_db": "used",
            "saved_to": "secondary_incidents.db",
            "message": "Primary incidents.db failed. Incident saved to secondary_incidents.db",
        }
    else:
        storage = {
            "incident_id": incident_id,
            "db_failover": False,
            "primary_db": "used",
            "secondary_db": "not_used",
            "saved_to": "incidents.db",
            "message": "Incident saved to primary incidents.db",
        }
    return incident_id, storage


@traceable(name="Notification Agent")
def notification_node(state):
    state.setdefault("flow", [])
    diagnosis = state.get("diagnosis", {}) or {}
    healing = state.get("healing", {}) or {}
    verification = state.get("verification", {}) or {}
    failure_type = state.get("failure_type", "success")

    critical_failures = [
        "invalid_api_key",
        "database_down",
    ]

    needs_manual = failure_type in critical_failures

    incident = {
        "city": state.get("city", "unknown"),
        "error_type": diagnosis.get("error_type", "UNKNOWN") if isinstance(diagnosis, dict) else "UNKNOWN",
        "severity": diagnosis.get("severity", "MEDIUM") if isinstance(diagnosis, dict) else "MEDIUM",
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

    storage_raw = save_incident(incident)
    incident_id, incident_storage = _normalise_storage_result(storage_raw)

    state["incident_id"] = incident_id
    state["incident_storage"] = incident_storage

    if incident_storage.get("db_failover"):
        state["flow"].append({
            "step": "database_failover",
            "status": "SUCCESS",
            "message": "Primary incidents.db failed. Incident saved to secondary_incidents.db",
        })
    else:
        state["flow"].append({
            "step": "database_storage",
            "status": "SAVED",
            "message": "Incident saved to primary incidents.db",
        })

    ticket = {"status": "NOT_REQUIRED"}
    if needs_manual:
        body = llm.ticket_body(state)
        ticket = tickets.send_ticket(
            subject=f"🚨 Manual Investigation Required: Weather API incident #{incident_id}",
            body=body,
        )
        ticket["body"] = body
        update_ticket(incident_id, ticket.get("status", "UNKNOWN"), body)
        state["flow"].append({
            "step": "ticket",
            "status": ticket.get("status"),
            "message": "Manual investigation ticket created",
        })

    incident["id"] = incident_id
    incident["ticket_status"] = ticket.get("status")
    incident["incident_storage"] = incident_storage
    app_state.last_incident = incident
    app_state.total_incidents += 1

    if healing.get("status") in ["SUCCESS", "HEALED"] and verification.get("status") == "SUCCESS":
        app_state.total_healed += 1

    state["ticket"] = ticket
    state["notification"] = {
        "status": "SAVED",
        "incident": incident,
        "incident_storage": incident_storage,
    }
    state["flow"].append({
        "step": "notification",
        "status": "SAVED",
        "message": f"Incident saved in SQLite with ID {incident_id} ({incident_storage.get('saved_to')})",
    })
    return state
