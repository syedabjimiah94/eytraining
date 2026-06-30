from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    city: str
    mode: str
    attempts: list[dict[str, Any]]
    primary_response: dict[str, Any]
    final_response: dict[str, Any]
    error: str
    diagnosis: dict[str, Any]
    healing: dict[str, Any]
    verification: dict[str, Any]
    notification: dict[str, Any]
    ticket: dict[str, Any]
    incident_id: int
    flow: list[dict[str, Any]]
    failure_type: str
