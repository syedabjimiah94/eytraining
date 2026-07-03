from fastapi import APIRouter, HTTPException
from app.database.database import list_incidents, get_incident

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("")
def get_incidents(limit: int = 20):
    return list_incidents(limit)


@router.get("/{incident_id}")
def read_incident(incident_id: int):
    incident = get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
