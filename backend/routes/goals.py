from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.goal_service import goal_service
from schemas.goal_schemas import GoalCreate, GoalResponse, NutritionRecommendation

router = APIRouter(prefix="/api/goals", tags=["Goals"])


@router.post("")
async def create_or_update_goal(
    user_id: str = Query(..., description="User's UUID"),
    goal_data: GoalCreate = ...
):
    """
    Create or update user goal
    
    Args:
        user_id: User's UUID
        goal_data: Goal data including goal_type and optional target_calories
        
    Returns:
        Created/updated goal
    """
    try:
        goal = await goal_service.create_or_update_goal(
            user_id=user_id,
            goal_type=goal_data.goal_type,
            target_calories=goal_data.target_calories
        )
        return goal
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create/update goal: {str(e)}")


@router.get("")
async def get_user_goal(
    user_id: str = Query(..., description="User's UUID")
):
    """
    Get user's active goal
    
    Args:
        user_id: User's UUID
        
    Returns:
        Active goal or None
    """
    try:
        goal = await goal_service.get_active_goal(user_id)
        if not goal:
            return {"message": "No active goal found", "goal": None}
        return goal
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch goal: {str(e)}")


@router.get("/recommendations", response_model=NutritionRecommendation)
async def get_nutrition_recommendations(
    goal_type: str = Query(..., description="Goal type: maintain, lose_weight, gain_weight, diabetes_management")
):
    """
    Get personalized nutrition recommendations based on goal type
    
    Args:
        goal_type: Type of goal
        
    Returns:
        Personalized recommendations
    """
    try:
        recommendations = await goal_service.get_nutrition_recommendations(goal_type)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recommendations: {str(e)}")


@router.post("/calculate-calories")
async def calculate_target_calories(
    user_id: str = Query(..., description="User's UUID"),
    current_weight: Optional[float] = Query(None, description="Current weight in kg"),
    target_weight: Optional[float] = Query(None, description="Target weight in kg"),
    height: Optional[float] = Query(None, description="Height in cm"),
    age: Optional[int] = Query(None, description="Age in years"),
    activity_level: str = Query("moderate", description="Activity level: sedentary, light, moderate, active, very_active")
):
    """
    Calculate personalized target daily calories
    
    Uses Harris-Benedict equation when user data is provided,
    otherwise uses goal-based defaults
    
    Returns:
        Recommended daily calorie target
    """
    try:
        target_calories = await goal_service.calculate_target_calories(
            user_id=user_id,
            current_weight=current_weight,
            target_weight=target_weight,
            height=height,
            age=age,
            activity_level=activity_level
        )
        return {
            "user_id": user_id,
            "target_calories": target_calories,
            "activity_level": activity_level
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate calories: {str(e)}")

