from typing import TypedDict

from langgraph.graph import StateGraph, END

from agents import (
    planner_agent,
    executor_agent,
    verifier_agent
)

class AgentState(TypedDict):
    query: str
    plan: str
    result: str
    verification: str
    final_answer: str


def planner_node(state):

    return {
        "plan": planner_agent(state["query"])
    }


def executor_node(state):

    return {
        "result": executor_agent(state["plan"])
    }


def verifier_node(state):

    return {
        "verification": verifier_agent(
            state["query"],
            state["result"]
        )
    }


def final_node(state):

    return {
        "final_answer": state["result"]
    }


def router(state):

    if "PASS" in state["verification"].upper():
        return "final"

    return "executor"


builder = StateGraph(AgentState)

builder.add_node("planner", planner_node)
builder.add_node("executor", executor_node)
builder.add_node("verifier", verifier_node)
builder.add_node("final", final_node)

builder.set_entry_point("planner")

builder.add_edge("planner", "executor")
builder.add_edge("executor", "verifier")

builder.add_conditional_edges(
    "verifier",
    router,
    {
        "executor": "executor",
        "final": "final"
    }
)

builder.add_edge("final", END)

graph = builder.compile()