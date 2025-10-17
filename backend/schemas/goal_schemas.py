from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class GoalBase(BaseModel):
    """Base goal schema"""
    goal_type: str  # 'maintain', 'lose_weight', 'gain_weight', 'diabetes_management'
    target_calories: Optional[int] = None


class GoalCreate(GoalBase):
    """Schema for creating a user goal"""
    pass


class GoalResponse(GoalBase):
    """Goal response schema"""
    id: UUID
    user_id: UUID
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class NutritionRecommendation(BaseModel):
    """Personalized nutrition recommendations"""
    title: str
    daily_calories: str
    focus: list[str]
    tips: str


class DailySummaryResponse(BaseModel):
    """Daily nutrition summary response"""
    date: str
    fruits_count: int
    vegetables_count: int
    protein_count: int
    dairy_count: int
    grains_count: int
    total_calories: int
    completion_percentage: int


class WeeklySummaryResponse(BaseModel):
    """Weekly nutrition summary"""
    week_start: str
    week_end: str
    daily_summaries: list[DailySummaryResponse]
    average_completion: float
    total_logs: int


class MissingFoodGroupsResponse(BaseModel):
    """Response for missing food groups"""
    date: str
    missing_groups: list[str]
    completed_groups: list[str]
    completion_percentage: int
    message: str


class StreakResponse(BaseModel):
    """User streak response"""
    current_streak: int
    longest_streak: int
    last_logged_date: Optional[str]
    message: str

