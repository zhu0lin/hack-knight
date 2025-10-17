from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class FoodCategory(str, Enum):
    """Food category enumeration"""
    FRUIT = "fruit"
    VEGETABLE = "vegetable"
    PROTEIN = "protein"
    DAIRY = "dairy"
    GRAIN = "grain"
    OTHER = "other"


class MealType(str, Enum):
    """Meal type enumeration"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class FoodLog:
    """Food log data model representing food_logs table in Supabase"""
    
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        image_url: str,
        detected_food_name: str,
        food_category: FoodCategory,
        healthiness_score: int,
        logged_at: datetime,
        created_at: datetime,
        calories: Optional[int] = None,
        meal_type: Optional[MealType] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.image_url = image_url
        self.detected_food_name = detected_food_name
        self.food_category = food_category
        self.healthiness_score = healthiness_score
        self.calories = calories
        self.meal_type = meal_type
        self.logged_at = logged_at
        self.created_at = created_at

