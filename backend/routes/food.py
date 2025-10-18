from fastapi import APIRouter, Query, HTTPException, UploadFile, File, Form
from typing import Optional
from datetime import date
import base64
from services.food_service import food_service
from services.storage_service import storage_service
from services.ml_service import ml_service
from schemas.food_schemas import FoodUploadResponse

router = APIRouter(prefix="/api/food", tags=["Food Logging"])


@router.post("/upload", response_model=FoodUploadResponse)
async def upload_food_image(
    image: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    meal_type: Optional[str] = Form(None)
):
    """
    Upload food image and analyze with ML
    
    This endpoint accepts:
    - image: The food image file
    - user_id: Optional user ID (None for anonymous users)
    - meal_type: Optional meal type (breakfast, lunch, dinner, snack)
    
    Returns:
    - Food log entry with ML analysis results
    """
    try:
        # Read image file
        image_bytes = await image.read()
        
        # Determine file extension
        file_extension = "jpg"
        if image.filename:
            ext = image.filename.split(".")[-1].lower()
            if ext in ["jpg", "jpeg", "png", "gif", "webp"]:
                file_extension = ext
        
        # Upload image to storage
        image_url = await storage_service.upload_food_image(
            user_id=user_id,
            image_data=image_bytes,
            file_extension=file_extension
        )
        
        # Analyze image with ML service
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        ml_result = await ml_service.analyze_food_image(image_base64)
        
        # Create food log entry
        food_log = await food_service.create_food_log(
            user_id=user_id,
            image_url=image_url,
            detected_food_name=ml_result["food_name"],
            food_category=ml_result["category"],
            healthiness_score=ml_result["healthiness_score"],
            calories=ml_result.get("calories"),
            meal_type=meal_type
        )
        
        return FoodUploadResponse(
            log_id=food_log["id"],
            image_url=image_url,
            detected_food_name=ml_result["food_name"],
            food_category=ml_result["category"],
            healthiness_score=ml_result["healthiness_score"],
            calories=ml_result.get("calories"),
            meal_type=meal_type,
            confidence=ml_result.get("confidence"),
            message="Food image uploaded and analyzed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload and analyze food image: {str(e)}")


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

