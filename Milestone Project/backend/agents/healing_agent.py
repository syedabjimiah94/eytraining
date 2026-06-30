import json
import time
from pathlib import Path

from app.weather_service import get_weather
from app.failure_simulator import simulate_failure

class HealingAgent:

    def __init__(
        self,
        diagnosis_log="logs/diagnosis.log",
        healing_log="logs/healing.log",
        max_retries=2
    ):

        self.diagnosis_log = Path(diagnosis_log)
        self.healing_log = Path(healing_log)
        self.max_retries = max_retries

    # ------------------------------------------------
    # Read latest diagnosis
    # ------------------------------------------------
    def read_latest_diagnosis(self):

        if not self.diagnosis_log.exists():
            return None

        with open(self.diagnosis_log, "r") as f:
            lines = f.readlines()

        if not lines:
            return None

        return json.loads(lines[-1])

    # ------------------------------------------------
    # Retry Weather API
    # ------------------------------------------------
    def retry_weather_api(self, city, failure_mode):

        for attempt in range(1, self.max_retries + 1):

            print(f"Retry Attempt : {attempt}")

            response = get_weather(city)
            response = simulate_failure(
                                        city,
                                        response,
                                        failure_mode
                                    )

            if response.get("status") == "SUCCESS":

                return {
                    "status": "SUCCESS",
                    "attempt": attempt,
                    "response": response
                }

            time.sleep(3)

        return {
            "status": "FAILED",
            "attempt": self.max_retries,
            "response": response
        }

    # ------------------------------------------------
    # Main Healing Logic
    # ------------------------------------------------
    def run(self):

        diagnosis = self.read_latest_diagnosis()

        if diagnosis is None:
            return None

        city = diagnosis["city"]
        failure_mode = diagnosis["failure_mode"]

        retry = self.retry_weather_api(
                            city,
                            diagnosis["failure_mode"]
                        )

        if retry["status"] == "SUCCESS":

            result = {

                "status": "SUCCESS",

                "city": city,

                "action": "AUTO_HEALED",

                "retry_attempt": retry["attempt"],

                "message": "Weather API recovered successfully.",
                "weather": retry["response"]
            }

        else:

            result = {

                "status": "FAILED",

                "city": city,

                "action": "ESCALATE",

                "retry_attempt": retry["attempt"],

                "message": "Retry failed. Escalate incident.",

                "response": retry["response"]
            }

        self.save(result)

        return result

    # ------------------------------------------------
    # Save Healing Log
    # ------------------------------------------------
    def save(self, result):

        self.healing_log.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(self.healing_log, "a") as f:

            f.write(json.dumps(result) + "\n")