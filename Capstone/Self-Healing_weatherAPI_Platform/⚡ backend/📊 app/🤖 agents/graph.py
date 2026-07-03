from langgraph.graph import StateGraph, END
from app.agents.state import WorkflowState
from app.agents.monitor_agent import monitoring_node
from app.agents.diagnosis_agent import diagnosis_node
from app.agents.healing_agent import healing_node
from app.agents.validator_agent import validator_node
from app.agents.notification_agent import notification_node
from langsmith import traceable

def monitor_router(state: WorkflowState):
    if state.get("error"):
        return "diagnosis"
    return END


def validation_router(state: WorkflowState):
    # Always notify after failure path so SQLite has the audit trail.
    return "notification"


builder = StateGraph(WorkflowState)
builder.add_node("monitor", monitoring_node)
builder.add_node("diagnosis", diagnosis_node)
builder.add_node("healing", healing_node)
builder.add_node("validate", validator_node)
builder.add_node("notification", notification_node)
builder.set_entry_point("monitor")
builder.add_conditional_edges("monitor", monitor_router, {"diagnosis": "diagnosis", END: END})
builder.add_edge("diagnosis", "healing")
builder.add_edge("healing", "validate")
builder.add_conditional_edges("validate", validation_router, {"notification": "notification"})
builder.add_edge("notification", END)
workflow = builder.compile()

@traceable(name="Self Healing Workflow")
def run_self_healing_workflow(
    city: str,
    mode: str | None = None,
    failure_type: str = "success"
):
    return workflow.invoke({
        "city": city,
        "mode": mode,
        "failure_type": failure_type,
        "flow": []
    })
