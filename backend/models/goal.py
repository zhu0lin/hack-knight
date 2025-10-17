from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class GoalType(str, Enum):
    """User goal type enumeration"""
    MAINTAIN = "maintain"
    LOSE_WEIGHT = "lose_weight"
    GAIN_WEIGHT = "gain_weight"
    DIABETES_MANAGEMENT = "diabetes_management"


class UserGoal:
    """User goal data model representing user_goals table in Supabase"""
    
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        goal_type: GoalType,
        created_at: datetime,
        is_active: bool = True,
        target_calories: Optional[int] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.goal_type = goal_type
        self.target_calories = target_calories
        self.created_at = created_at
        self.is_active = is_active

