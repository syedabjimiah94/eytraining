import json
import os
from pathlib import Path
from datetime import datetime

import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")


class NotificationAgent:

    def __init__(
        self,
        healing_log="logs/healing.log",
        notification_log="logs/notification.log"
    ):

        self.healing_log = Path(healing_log)
        self.notification_log = Path(notification_log)

    # ----------------------------------------
    # Read latest healing result
    # ----------------------------------------
    def read_latest_healing(self):

        if not self.healing_log.exists():
            return None

        with open(self.healing_log, "r") as f:

            lines = f.readlines()

        if not lines:
            return None

        return json.loads(lines[-1])

    # ----------------------------------------
    # Generate Ticket
    # ----------------------------------------
    def generate_ticket(self, healing):

        return {

            "ticket_id": "INC-" + datetime.now().strftime("%Y%m%d%H%M%S"),

            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            "city": healing["city"],

            "status": healing["status"],

            "action": healing["action"],

            "retry_attempt": healing["retry_attempt"],

            "priority": "HIGH"
        }

    # ----------------------------------------
    # Send Email
    # ----------------------------------------
    def send_email(self, ticket):

        resend.Emails.send({

            "from": os.getenv("FROM_EMAIL"),

            "to": [os.getenv("TO_EMAIL")],

            "subject": f"🚨 AutoHealAI Incident - {ticket['ticket_id']}",

            "html": f"""

            <h2>🚨 AutoHealAI Incident</h2>

            <table border="1" cellpadding="8">

                <tr>
                    <td><b>Ticket ID</b></td>
                    <td>{ticket['ticket_id']}</td>
                </tr>

                <tr>
                    <td><b>City</b></td>
                    <td>{ticket['city']}</td>
                </tr>

                <tr>
                    <td><b>Status</b></td>
                    <td>{ticket['status']}</td>
                </tr>

                <tr>
                    <td><b>Retry Attempt</b></td>
                    <td>{ticket['retry_attempt']}</td>
                </tr>

                <tr>
                    <td><b>Priority</b></td>
                    <td>{ticket['priority']}</td>
                </tr>

                <tr>
                    <td><b>Time</b></td>
                    <td>{ticket['timestamp']}</td>
                </tr>

            </table>

            <br>

            <h3 style="color:red">
                Manual Investigation Required
            </h3>

            """

        })

    # ----------------------------------------
    # Save notification
    # ----------------------------------------
    def save(self, ticket):

        self.notification_log.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(self.notification_log, "a") as f:

            f.write(json.dumps(ticket) + "\n")

    # ----------------------------------------
    # Main
    # ----------------------------------------
    def run(self):

        healing = self.read_latest_healing()

        if healing is None:
            return None

        if healing["status"] == "SUCCESS":
            return None

        ticket = self.generate_ticket(healing)

        self.send_email(ticket)

        self.save(ticket)

        return ticket