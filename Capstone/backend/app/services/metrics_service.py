import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "database" / "incidents.db"


class MetricsService:

    def __init__(self):
        self.init_db()

    def connect(self):
        return sqlite3.connect(DB_PATH)

    def init_db(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS app_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    requests INTEGER DEFAULT 0,
                    success INTEGER DEFAULT 0,
                    self_healed INTEGER DEFAULT 0,
                    manual INTEGER DEFAULT 0,
                    total_latency_ms REAL DEFAULT 0,
                    llm_calls INTEGER DEFAULT 0,
                    emails_sent INTEGER DEFAULT 0
                )
            """)

            row = conn.execute("SELECT COUNT(*) FROM app_metrics").fetchone()

            if row[0] == 0:
                conn.execute("""
                    INSERT INTO app_metrics
                    (requests, success, self_healed, manual, total_latency_ms, llm_calls, emails_sent)
                    VALUES (0, 0, 0, 0, 0, 0, 0)
                """)

            conn.commit()

    def record(self, response: dict):
        latency_ms = response.get("latency_ms", 0) or 0

        healing = response.get("healing", {}) or {}
        diagnosis = response.get("diagnosis", {}) or {}
        ticket = response.get("ticket", {}) or {}

        is_self_healed = bool(response.get("healed")) or healing.get("status") == "SUCCESS"
        is_manual = ticket.get("status") in ["SENT", "FAILED", "NOT_SENT"]

        success = 1 if not is_manual else 0
        self_healed = 1 if is_self_healed else 0
        manual = 1 if is_manual else 0

        llm_calls = 0
        if diagnosis.get("llm_used"):
            llm_calls += 1

        plan = healing.get("plan", {})
        if isinstance(plan, dict) and plan.get("llm_used"):
            llm_calls += 1

        emails_sent = 1 if ticket.get("status") == "SENT" else 0

        with self.connect() as conn:
            conn.execute("""
                UPDATE app_metrics
                SET requests = requests + 1,
                    success = success + ?,
                    self_healed = self_healed + ?,
                    manual = manual + ?,
                    total_latency_ms = total_latency_ms + ?,
                    llm_calls = llm_calls + ?,
                    emails_sent = emails_sent + ?
                WHERE id = 1
            """, (
                success,
                self_healed,
                manual,
                latency_ms,
                llm_calls,
                emails_sent
            ))
            conn.commit()

    def get_metrics(self):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM app_metrics WHERE id = 1").fetchone()

        requests = row["requests"]

        avg_latency_sec = 0
        if requests > 0:
            avg_latency_sec = round((row["total_latency_ms"] / requests) / 1000, 2)

        return {
            "requests": row["requests"],
            "success": row["success"],
            "self_healed": row["self_healed"],
            "manual": row["manual"],
            "average_latency_sec": avg_latency_sec,
            "llm_calls": row["llm_calls"],
            "emails_sent": row["emails_sent"]
        }