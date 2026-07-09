from fastapi import APIRouter
from app.database.database import (
    list_request_logs,
    delete_request_log_by_request_id,
)

router = APIRouter(prefix="/request-logs", tags=["Request Logs"])


@router.get("")
def get_request_logs(limit: int = 30):
    return list_request_logs(limit)

@router.delete("/{request_id}")
def delete_request_log(request_id: str):
    deleted = delete_request_log_by_request_id(request_id)

    if deleted:
        return {
            "status": "SUCCESS",
            "message": "Request log deleted successfully.",
            "request_id": request_id,
        }

    return {
        "status": "FAILED",
        "message": "Request ID not found.",
        "request_id": request_id,
    }