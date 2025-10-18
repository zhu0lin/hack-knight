from datetime import datetime, date
from uuid import UUID


class UserStreak:
    """User streak data model representing user_streaks table in Supabase"""
    
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        current_streak: int,
        longest_streak: int,
        last_logged_date: date,
        updated_at: datetime,
    ):
        self.id = id
        self.user_id = user_id
        self.current_streak = current_streak
        self.longest_streak = longest_streak
        self.last_logged_date = last_logged_date
        self.updated_at = updated_at


class DailyNutritionSummary:
    """Daily nutrition summary model representing daily_nutrition_summary table"""
    
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        date: date,
        fruits_count: int,
        vegetables_count: int,
        protein_count: int,
        dairy_count: int,
        grains_count: int,
        total_calories: int,
        completion_percentage: int,
        created_at: datetime,
    ):
        self.id = id
        self.user_id = user_id
        self.date = date
        self.fruits_count = fruits_count
        self.vegetables_count = vegetables_count
        self.protein_count = protein_count
        self.dairy_count = dairy_count
        self.grains_count = grains_count
        self.total_calories = total_calories
        self.completion_percentage = completion_percentage
        self.created_at = created_at

