import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent / "incidents.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
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


def save_incident(incident: dict[str, Any]) -> int:
    init_db()
    with get_connection() as conn:
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
    init_db()
    with get_connection() as conn:
        conn.execute(
            "UPDATE incidents SET ticket_status = ?, ticket_body = ? WHERE id = ?",
            (ticket_status, ticket_body, incident_id),
        )
        conn.commit()


def list_incidents(limit: int = 20) -> list[dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM incidents ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        data = []
        for row in rows:
            item = dict(row)
            for key in ("diagnosis_json", "attempts_json", "flow_json"):
                if item.get(key):
                    try:
                        item[key.replace("_json", "")] = json.loads(item[key])
                    except Exception:
                        pass
            data.append(item)
        return data


def get_incident(incident_id: int) -> dict[str, Any] | None:
    init_db()
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
        if not row:
            return None
        item = dict(row)
        for key in ("diagnosis_json", "attempts_json", "flow_json"):
            if item.get(key):
                item[key.replace("_json", "")] = json.loads(item[key])
        return item
