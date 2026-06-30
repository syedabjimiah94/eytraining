from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Incident(BaseModel):
    id: Optional[int] = None
    city: str
    error_type: str
    message: str
    status: str
    action_taken: str
    created_at: datetime
