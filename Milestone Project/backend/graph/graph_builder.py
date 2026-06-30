from langgraph.graph import StateGraph, END

from graph.state import WorkflowState
from graph.nodes import (
    monitoring_node,
    diagnosis_node,
    healing_node,
    verification_node,
    notification_node
)


def monitoring_router(state):

    incident = state["monitoring"]

    if incident is None:
        return END

    if incident["status"] == "SUCCESS":
        return END

    return "diagnosis"


def healing_router(state):

    if state["healing"]["status"] == "SUCCESS":
        return "verification"

    return "notification"


def verification_router(state):

    if state["verification"]["status"] == "SUCCESS":
        return END

    return "notification"


builder = StateGraph(WorkflowState)

builder.add_node("monitoring", monitoring_node)
builder.add_node("diagnosis", diagnosis_node)
builder.add_node("healing", healing_node)
builder.add_node("verification", verification_node)
builder.add_node("notification", notification_node)

builder.set_entry_point("monitoring")

builder.add_conditional_edges(
    "monitoring",
    monitoring_router
)

builder.add_edge(
    "diagnosis",
    "healing"
)

builder.add_conditional_edges(
    "healing",
    healing_router
)

builder.add_conditional_edges(
    "verification",
    verification_router
)

builder.add_edge(
    "notification",
    END
)

graph = builder.compile()