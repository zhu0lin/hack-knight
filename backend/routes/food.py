from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from services.food_service import food_service
from utils.dependencies import get_current_user_id

router = APIRouter(prefix="/api/food", tags=["Food Logging"])


@router.post("/upload")
async def upload_food_image():
    """Upload food image and analyze with ML"""
    return {"message": "Food upload endpoint - to be implemented"}


@router.get("/logs")
async def get_food_logs(
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(100, ge=1, le=500),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    """
    Return the authenticated user's food logs, optionally filtered by date range.
    """
    try:
        logs = await food_service.get_food_logs(
            user_id=user_id,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
        )
        return {"logs": logs}
    except Exception as exc:
        detail = "Not authenticated" if str(exc).lower().startswith("missing authorization") else f"Failed to fetch food logs: {exc}"
        status_code = status.HTTP_401_UNAUTHORIZED if detail == "Not authenticated" else status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=status_code, detail=detail) from exc


@router.get("/logs/{log_id}")
async def get_food_log(log_id: str):
    """Get specific food log"""
    return {"message": f"Get food log {log_id} endpoint - to be implemented"}


@router.delete("/logs/{log_id}")
async def delete_food_log(log_id: str):
    """Delete food log"""
    return {"message": f"Delete food log {log_id} endpoint - to be implemented"}


@router.put("/logs/{log_id}")
async def update_food_log(log_id: str):
    """Edit food log details"""
    return {"message": f"Update food log {log_id} endpoint - to be implemented"}
