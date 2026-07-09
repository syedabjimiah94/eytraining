import json
import sqlite3
from pathlib import Path
from typing import Any
from datetime import datetime

from app.state.simulator_state import simulator_state

DB_PATH = Path(__file__).parent / "incidents.db"
SECONDARY_DB_PATH = Path(__file__).parent / "secondary_incidents.db"


def get_connection(db_path: Path = DB_PATH):
    return sqlite3.connect(db_path)


def init_db(db_path: Path = DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                error_type TEXT NOT NULL,
                severity TEXT,
                message TEXT NOT NULL,
                status TEXT NOT NULL,
                action_taken TEXT NOT NULL,
                diagnosis_json TEXT,
                attempts_json TEXT,
                flow_json TEXT,
                ticket_status TEXT,
                ticket_body TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT,
                city TEXT NOT NULL,
                mode TEXT,
                failure_type TEXT,
                final_status TEXT,
                error_type TEXT,
                diagnosis TEXT,
                healing_action TEXT,
                validation_result TEXT,
                incident_id INTEGER,
                latency_ms REAL,
                created_at TEXT NOT NULL
            )
            """
        )
        # Safe migrations for older DB created in previous phase
        existing = {row[1] for row in conn.execute("PRAGMA table_info(incidents)").fetchall()}
        columns = {
            "severity": "TEXT",
            "diagnosis_json": "TEXT",
            "attempts_json": "TEXT",
            "flow_json": "TEXT",
            "ticket_status": "TEXT",
            "ticket_body": "TEXT",
        }
        for column, typ in columns.items():
            if column not in existing:
                conn.execute(f"ALTER TABLE incidents ADD COLUMN {column} {typ}")
        conn.commit()


# def save_incident(incident: dict[str, Any]) -> int:
#     """Save incident to primary DB. If primary DB is simulated down or fails,
#     automatically fail over and save the same incident to secondary_incidents.db.
#     """
#     try:
#         if simulator_state.database_down:
#             raise sqlite3.OperationalError("Simulated primary incidents.db failure")

#         incident_id = _save_incident_to_db(incident, DB_PATH)
#         print(f"[DB] Incident saved in primary incidents.db with ID {incident_id}")
#         return incident_id

#     except Exception as primary_error:
#         print("===================================================")
#         print(f"[DB-FAILOVER] Primary DB failed: {primary_error}")
#         print("[DB-FAILOVER] Switching to secondary_incidents.db")
#         print("===================================================")

#         incident_id = _save_incident_to_db(incident, SECONDARY_DB_PATH)
#         print(f"[DB-FAILOVER] Incident saved in secondary_incidents.db with ID {incident_id}")
#         return incident_id

def save_incident(incident: dict[str, Any]) -> dict[str, Any]:
    try:
        if simulator_state.database_down:
            raise sqlite3.OperationalError("Simulated primary incidents.db failure")

        incident_id = _save_incident_to_db(incident, DB_PATH)

        return {
            "incident_id": incident_id,
            "db_failover": False,
            "primary_db": "used",
            "secondary_db": "not_used",
            "saved_to": "incidents.db",
            "message": "Incident saved to primary incidents.db"
        }

    except Exception as primary_error:
        print("===================================================")
        print(f"[DB-FAILOVER] Primary DB failed: {primary_error}")
        print("[DB-FAILOVER] Switching to secondary_incidents.db")
        print("===================================================")

        incident_id = _save_incident_to_db(incident, SECONDARY_DB_PATH)

        return {
            "incident_id": incident_id,
            "db_failover": True,
            "primary_db": "failed",
            "secondary_db": "used",
            "saved_to": "secondary_incidents.db",
            "primary_error": str(primary_error),
            "message": "Primary DB failed. Incident saved to secondary_incidents.db"
        }


def _save_incident_to_db(incident: dict[str, Any], db_path: Path) -> int:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO incidents(
                city, error_type, severity, message, status, action_taken,
                diagnosis_json, attempts_json, flow_json, ticket_status, ticket_body, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                incident["city"],
                incident["error_type"],
                incident.get("severity"),
                incident["message"],
                incident["status"],
                incident["action_taken"],
                json.dumps(incident.get("diagnosis", {})),
                json.dumps(incident.get("attempts", [])),
                json.dumps(incident.get("flow", [])),
                incident.get("ticket_status"),
                incident.get("ticket_body"),
                incident["created_at"],
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def update_ticket(incident_id: int, ticket_status: str, ticket_body: str):
    """Update ticket info in the DB that contains the incident.
    If primary DB is down or the row is not found there, update secondary DB.
    """
    try:
        if simulator_state.database_down:
            raise sqlite3.OperationalError("Simulated primary incidents.db failure")

        updated = _update_ticket_in_db(DB_PATH, incident_id, ticket_status, ticket_body)
        if updated:
            return

        _update_ticket_in_db(SECONDARY_DB_PATH, incident_id, ticket_status, ticket_body)

    except Exception as primary_error:
        print(f"[DB-FAILOVER] Primary ticket update failed: {primary_error}")
        _update_ticket_in_db(SECONDARY_DB_PATH, incident_id, ticket_status, ticket_body)


def _update_ticket_in_db(db_path: Path, incident_id: int, ticket_status: str, ticket_body: str) -> int:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "UPDATE incidents SET ticket_status = ?, ticket_body = ? WHERE id = ?",
            (ticket_status, ticket_body, incident_id),
        )
        conn.commit()
        return cur.rowcount


def _list_incidents_from_db(db_path: Path, limit: int, db_source: str) -> list[dict[str, Any]]:
    init_db(db_path)
    with get_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM incidents ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        data = []
        for row in rows:
            item = dict(row)
            item["db_source"] = db_source
            for key in ("diagnosis_json", "attempts_json", "flow_json"):
                if item.get(key):
                    try:
                        item[key.replace("_json", "")] = json.loads(item[key])
                    except Exception:
                        pass
            data.append(item)
        return data


def list_incidents(limit: int = 20, source: str = "primary") -> list[dict[str, Any]]:
    """List incidents from primary, secondary, or both.

    source values:
    - primary
    - secondary
    - both
    """
    if source == "secondary":
        return _list_incidents_from_db(SECONDARY_DB_PATH, limit, "secondary")

    if source == "both":
        primary = _list_incidents_from_db(DB_PATH, limit, "primary")
        secondary = _list_incidents_from_db(SECONDARY_DB_PATH, limit, "secondary")
        return sorted(
            primary + secondary,
            key=lambda x: x.get("created_at", ""),
            reverse=True,
        )[:limit]

    return _list_incidents_from_db(DB_PATH, limit, "primary")


def get_incident(incident_id: int) -> dict[str, Any] | None:
    # Try primary first, then secondary. This keeps existing API behaviour working
    # even when the incident was created during DB failover.
    for db_path, db_source in ((DB_PATH, "primary"), (SECONDARY_DB_PATH, "secondary")):
        init_db(db_path)
        with get_connection(db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
            if row:
                item = dict(row)
                item["db_source"] = db_source
                for key in ("diagnosis_json", "attempts_json", "flow_json"):
                    if item.get(key):
                        try:
                            item[key.replace("_json", "")] = json.loads(item[key])
                        except Exception:
                            pass
                return item
    return None


def save_request_log(log: dict[str, Any]) -> int:
    init_db()
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO request_logs (
                request_id, city, mode, failure_type, final_status,
                error_type, diagnosis, healing_action, validation_result,
                incident_id, latency_ms, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                log.get("request_id"),
                log.get("city"),
                log.get("mode"),
                log.get("failure_type"),
                log.get("final_status"),
                log.get("error_type"),
                log.get("diagnosis"),
                log.get("healing_action"),
                log.get("validation_result"),
                log.get("incident_id"),
                log.get("latency_ms"),
                log.get("created_at", datetime.utcnow().isoformat()),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_request_logs(limit: int = 30) -> list[dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM request_logs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def delete_request_log_by_request_id(request_id: str) -> int:
    init_db()
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM request_logs WHERE request_id = ?",
            (request_id,),
        )
        conn.commit()
        return cur.rowcount
