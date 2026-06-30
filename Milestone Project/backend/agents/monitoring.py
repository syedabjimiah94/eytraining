# from datetime import datetime


# class MonitoringAgent:
#     """
#     Monitors Weather API responses
#     and generates an incident report.
#     """

#     def monitor(self, city: str, api_response: dict):

#         incident = {
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "city": city,
#             "status": api_response.get("status")
#         }

#         # Success
#         if api_response["status"] == "SUCCESS":

#             incident["severity"] = "INFO"
#             incident["message"] = "Weather API is healthy."

#         # Failure
#         else:

#             incident["severity"] = "HIGH"

#             incident["message"] = api_response.get(
#                 "error",
#                 api_response.get("message", "Unknown Error")
#             )

#         return incident


import json
import os
from datetime import datetime


class MonitoringAgent:

    def __init__(self):

        os.makedirs("logs", exist_ok=True)

        self.log_file = "logs/incident.log"

    def monitor(self, city: str, api_response: dict, failure_mode=None):

        incident = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "city": city,
            "status": api_response.get("status"),
            "failure_mode": failure_mode
        }

        if api_response["status"] == "SUCCESS":

            incident["severity"] = "INFO"
            incident["message"] = "Weather API is healthy."

        else:

            incident["severity"] = "HIGH"

            incident["message"] = api_response.get(
                "error",
                api_response.get("message", "Unknown Error")
            )

        # Save incident
        with open(self.log_file, "a") as f:
            f.write(json.dumps(incident) + "\n")

        return incident