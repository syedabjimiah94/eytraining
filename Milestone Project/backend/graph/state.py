from typing import TypedDict, Optional


class WorkflowState(TypedDict):

    city: str
    failure_mode: Optional[str]
    weather_result: dict

    monitoring: Optional[dict]
    diagnosis: Optional[dict]
    healing: Optional[dict]
    verification: Optional[dict]
    ticket: Optional[dict]