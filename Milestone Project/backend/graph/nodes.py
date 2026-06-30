from agents.monitoring import MonitoringAgent
from agents.diagnosis_agent import DiagnosisAgent
from agents.healing_agent import HealingAgent
from agents.verification_agent import VerificationAgent
from agents.notification_agent import NotificationAgent
from langsmith import traceable

monitor = MonitoringAgent()
diagnosis = DiagnosisAgent()
healing = HealingAgent()
verification = VerificationAgent()
notification = NotificationAgent()

@traceable(name="Monitoring Agent")
def monitoring_node(state):

    incident = monitor.monitor(
        state["city"],
        state["weather_result"],
        state["failure_mode"]
    )

    state["monitoring"] = incident
    return state

@traceable(name="Diagnosis Agent")
def diagnosis_node(state):

    state["diagnosis"] = diagnosis.run()
    return state

@traceable(name="Healing Agent")
def healing_node(state):

    state["healing"] = healing.run()
    return state

@traceable(name="Verification Agent")
def verification_node(state):

    state["verification"] = verification.run()
    return state

@traceable(name="Notification Agent")
def notification_node(state):

    state["ticket"] = notification.run()
    return state