import json
from pathlib import Path
from datetime import datetime

from app.weather_service import get_weather


class VerificationAgent:

    def __init__(
        self,
        healing_log="logs/healing.log",
        verification_log="logs/verification.log"
    ):

        self.healing_log = Path(healing_log)
        self.verification_log = Path(verification_log)

    # ---------------------------------------------
    # Read latest healing log
    # ---------------------------------------------
    def read_latest_healing(self):

        if not self.healing_log.exists():
            return None

        with open(self.healing_log, "r") as f:
            lines = f.readlines()

        if not lines:
            return None

        return json.loads(lines[-1])

    # ---------------------------------------------
    # Save verification log
    # ---------------------------------------------
    def save(self, result):

        self.verification_log.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(self.verification_log, "a") as f:
            f.write(json.dumps(result) + "\n")

    # ---------------------------------------------
    # Verify Weather API
    # ---------------------------------------------
    def run(self):

        healing = self.read_latest_healing()

        if healing is None:

            result = {

                "status": "FAILED",
                "verification": "FAILED",
                "message": "Healing log not found."

            }

            self.save(result)
            return result

        city = healing["city"]

        response = get_weather(city)

        if response["status"] == "SUCCESS":

            result = {

                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

                "city": city,

                "verification": "RECOVERED",

                "status": "SUCCESS"

            }

        else:

            result = {

                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

                "city": city,

                "verification": "FAILED",

                "status": "FAILED"

            }

        self.save(result)

        return result