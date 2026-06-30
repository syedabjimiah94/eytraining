from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    simulator_mode: str
