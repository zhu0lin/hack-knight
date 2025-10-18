from fastapi import APIRouter, HTTPException, Query
from datetime import date
from typing import Optional
from services.supabase_client import get_supabase

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/daily-summary/{user_id}")
async def get_daily_summary(
    user_id: str,
    date_filter: Optional[str] = Query(None, alias="date", description="Date in YYYY-MM-DD format, defaults to today")
):
    """
    Get daily nutrition summary for a specific user and date
    
    Returns counts for each food category and completion percentage
    """
    try:
        # Parse date or use today
        if date_filter:
            summary_date = date_filter
        else:
            summary_date = date.today().isoformat()
        
        supabase = get_supabase()
        
        # Get daily summary from database
        response = supabase.table("daily_nutrition_summary").select("*").eq("user_id", user_id).eq("date", summary_date).single().execute()
        
        if response.data:
            return response.data
        else:
            # If no summary exists, return zeros
            return {
                "user_id": user_id,
                "date": summary_date,
                "fruits_count": 0,
                "vegetables_count": 0,
                "protein_count": 0,
                "dairy_count": 0,
                "grains_count": 0,
                "total_calories": 0,
                "completion_percentage": 0
            }
    except Exception as e:
        # If summary doesn't exist or error, return default zeros
        return {
            "user_id": user_id,
            "date": summary_date if 'summary_date' in locals() else date.today().isoformat(),
            "fruits_count": 0,
            "vegetables_count": 0,
            "protein_count": 0,
            "dairy_count": 0,
            "grains_count": 0,
            "total_calories": 0,
            "completion_percentage": 0
        }


@router.get("/today")
async def get_today_summary():
    """Get today's nutrition summary"""
    return {"message": "Today's summary endpoint - to be implemented"}


@router.get("/week")
async def get_week_summary():
    """Get weekly nutrition summary"""
    return {"message": "Weekly summary endpoint - to be implemented"}


@router.get("/missing")
async def get_missing_food_groups():
    """Get what food groups are missing today"""
    return {"message": "Missing food groups endpoint - to be implemented"}


@router.get("/streak")
async def get_user_streak():
    """Get user's current streak"""
    return {"message": "User streak endpoint - to be implemented"}

