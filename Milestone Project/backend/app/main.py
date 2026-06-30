from fastapi import FastAPI
from app.weather_service import get_weather
from app.failure_simulator import simulate_failure
#middlewares
from middleware.app_middleware import AppMiddleware
#guardrails
from guardrails.validator import validate_city
#Agents
from agents.orchestrator_agent import OrchestratorAgent
from langsmith import traceable

app = FastAPI()

orchestrator = OrchestratorAgent()

#middlewares
app.add_middleware(AppMiddleware)

# @app.get("/weather/{city}")
# def weather(city: str, mode: str = None):
#     valid, city = validate_city(city)

#     if not valid:

#         return {
#             "status": "FAILED",
#             "message": city
#         }

#     result = get_weather(city)
#     final_result = simulate_failure(city, result, mode)
#     incident = monitoring_agent.monitor(city, final_result, mode)

#     # Run Diagnosis Agent only if monitoring detects a failure
#     diagnosis = None
#     healing = None
#     ticket = None
#     verification = None

#     if incident and incident.get("status") == "FAILED":

#         diagnosis_agent = DiagnosisAgent()
#         diagnosis = diagnosis_agent.run()

#         healing_agent = HealingAgent()
#         healing = healing_agent.run()
#         # if healing["status"] == "FAILED":
#         #     notification = NotificationAgent()
#         #     ticket = notification.run()
#         # Verify only if healing succeeded
#         if healing["status"] == "SUCCESS":

#             verification_agent = VerificationAgent()
#             verification = verification_agent.run()

#             if verification["status"] == "FAILED":

#                 notification = NotificationAgent()
#                 ticket = notification.run()

#         # Healing itself failed
#         else:

#             notification = NotificationAgent()
#             ticket = notification.run()

#     # return final_result

#     # User Response

#     user_response = {}

#     if healing:

#         if healing["status"] == "SUCCESS":

#             user_response = {

#                 "status": "SUCCESS",

#                 "message": "✅ AutoHeal AI recovered the Weather API successfully.",

#                 "weather": healing["weather"]

#             }

#         else:

#             user_response = {

#                 "status": "FAILED",

#                 "message": "❌ AutoHeal AI could not recover the Weather API. Support team has been notified."

#             }

#     else:

#         user_response = {

#             "status": "SUCCESS",

#             "message": "Weather retrieved successfully.",

#             "weather": final_result

#         }

#     return {

#         "user_response": user_response,

#         "workflow": {


#             "monitoring": incident,

#             "diagnosis": diagnosis,

#             "healing": healing,

#             "verification": verification,

#             "ticket": ticket

#         }

#     }

@app.get("/weather/{city}")
@traceable(name="Weather Endpoint")
def weather(city: str, mode: str = None):

    # -------------------------------
    # Guardrail Validation
    # -------------------------------
    valid, city = validate_city(city)

    if not valid:

        return {
            "status": "FAILED",
            "message": city
        }

    # -------------------------------
    # Weather Service
    # -------------------------------
    result = get_weather(city)

    final_result = simulate_failure(
        city,
        result,
        mode
    )

    # -------------------------------
    # Multi-Agent Orchestration
    # -------------------------------
    workflow = orchestrator.run(
        city=city,
        weather_result=final_result,
        failure_mode=mode
    )

    incident = workflow["incident"]
    diagnosis = workflow["diagnosis"]
    healing = workflow["healing"]
    verification = workflow["verification"]
    ticket = workflow["ticket"]

    # -------------------------------
    # User Response
    # -------------------------------
    if healing:

        if healing["status"] == "SUCCESS":

            user_response = {

                "status": "SUCCESS",

                "message": "✅ AutoHealAI recovered the Weather API successfully.",

                "weather": healing["weather"]

            }

        else:

            user_response = {

                "status": "FAILED",

                "message": "❌ AutoHealAI could not recover the Weather API. Support team has been notified."

            }

    else:

        user_response = {

            "status": "SUCCESS",

            "message": "Weather retrieved successfully.",

            "weather": final_result

        }

    return {

        "user_response": user_response,

        "workflow": {

            "monitoring": incident,

            "diagnosis": diagnosis,

            "healing": healing,

            "verification": verification,

            "ticket": ticket

        }

    }