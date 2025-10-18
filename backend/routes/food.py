from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import date
from services.food_service import food_service

router = APIRouter(prefix="/api/food", tags=["Food Logging"])


@router.post("/upload")
async def upload_food_image():
    """Upload food image and analyze with ML"""
    return {"message": "Food upload endpoint - to be implemented"}


@router.get("/logs")
async def get_food_logs(
    limit: int = Query(100, description="Maximum number of logs to return", ge=1, le=1000),
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)")
):
    """
    Get all food logs from all users
    
    Query Parameters:
    - limit: Maximum number of logs (default: 100, max: 1000)
    - start_date: Optional start date filter
    - end_date: Optional end date filter
    """
    try:
        logs = await food_service.get_all_food_logs(
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "logs": logs,
            "total": len(logs),
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch food logs: {str(e)}")


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

