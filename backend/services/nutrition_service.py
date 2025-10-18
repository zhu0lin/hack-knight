from typing import Dict, List
from datetime import date, timedelta
from services.supabase_client import get_supabase


class NutritionService:
    """Service for nutrition calculations and streak management"""
    
    def __init__(self):
        self.supabase = None
    
    def _get_supabase(self):
        """Lazy load Supabase client"""
        if self.supabase is None:
            self.supabase = get_supabase()
        return self.supabase
    
    async def get_missing_food_groups(self, user_id: str, target_date: date = None) -> List[str]:
        """
        Determine which food groups user is missing for a specific date
        
        Args:
            user_id: User's UUID
            target_date: Date to check (defaults to today)
            
        Returns:
            List of missing food group names
        """
        if target_date is None:
            target_date = date.today()
        
        try:
            response = self._get_supabase().table("daily_nutrition_summary").select("*").eq("user_id", user_id).eq("date", target_date.isoformat()).execute()
            
            if not response.data:
                return ["fruits", "vegetables", "protein", "dairy", "grains"]
            
            summary = response.data[0]
            missing = []
            
            if summary.get("fruits_count", 0) == 0:
                missing.append("fruits")
            if summary.get("vegetables_count", 0) == 0:
                missing.append("vegetables")
            if summary.get("protein_count", 0) == 0:
                missing.append("protein")
            if summary.get("dairy_count", 0) == 0:
                missing.append("dairy")
            if summary.get("grains_count", 0) == 0:
                missing.append("grains")
            
            return missing
        except Exception as e:
            print(f"Error getting missing food groups: {e}")
            return []
    
    async def calculate_streak(self, user_id: str) -> Dict:
        """
        Calculate and update user's streak
        
        Args:
            user_id: User's UUID
            
        Returns:
            Dict with current_streak and longest_streak
        """
        try:
            # Get all daily summaries ordered by date
            response = self._get_supabase().table("daily_nutrition_summary").select("*").eq("user_id", user_id).order("date", desc=True).execute()
            
            if not response.data:
                return {"current_streak": 0, "longest_streak": 0}
            
            summaries = response.data
            current_streak = 0
            longest_streak = 0
            temp_streak = 0
            
            # Calculate streaks (completion_percentage must be 100% to count)
            expected_date = date.today()
            
            for summary in summaries:
                summary_date = date.fromisoformat(summary["date"])
                
                # Check if this summary is for the expected date
                if summary_date == expected_date and summary.get("completion_percentage", 0) == 100:
                    temp_streak += 1
                    expected_date = expected_date - timedelta(days=1)
                else:
                    break
            
            current_streak = temp_streak
            
            # Calculate longest streak
            temp_streak = 0
            prev_date = None
            
            for summary in summaries:
                summary_date = date.fromisoformat(summary["date"])
                
                if summary.get("completion_percentage", 0) == 100:
                    if prev_date is None or (prev_date - summary_date).days == 1:
                        temp_streak += 1
                        longest_streak = max(longest_streak, temp_streak)
                    else:
                        temp_streak = 1
                else:
                    temp_streak = 0
                
                prev_date = summary_date
            
            # Update or create streak record
            streak_data = {
                "user_id": user_id,
                "current_streak": current_streak,
                "longest_streak": max(longest_streak, current_streak),
                "last_logged_date": date.today().isoformat(),
            }
            
            self._get_supabase().table("user_streaks").upsert(streak_data).execute()
            
            return {
                "current_streak": current_streak,
                "longest_streak": max(longest_streak, current_streak),
            }
        except Exception as e:
            print(f"Error calculating streak: {e}")
            return {"current_streak": 0, "longest_streak": 0}
    
    async def get_personalized_recommendations(self, user_id: str) -> Dict:
        """
        Generate personalized nutrition recommendations based on user's goal
        
        Args:
            user_id: User's UUID
            
        Returns:
            Dict with recommendations
        """
        try:
            # Get user's active goal
            goal_response = self._get_supabase().table("user_goals").select("*").eq("user_id", user_id).eq("is_active", True).execute()
            
            if not goal_response.data:
                return self._get_default_recommendations()
            
            goal = goal_response.data[0]
            goal_type = goal.get("goal_type")
            
            recommendations = {
                "maintain": {
                    "title": "Maintain Healthy Weight",
                    "daily_calories": "2000-2500",
                    "focus": ["Balanced meals from all food groups", "Regular portions", "Stay hydrated"],
                    "tips": "Aim for variety in your diet to ensure you're getting all nutrients."
                },
                "lose_weight": {
                    "title": "Weight Loss",
                    "daily_calories": "1500-2000",
                    "focus": ["High protein foods", "More vegetables and fruits", "Low-calorie options", "Smaller portions"],
                    "tips": "Focus on lean proteins and vegetables to feel full while reducing calories."
                },
                "gain_weight": {
                    "title": "Weight Gain",
                    "daily_calories": "2500-3000",
                    "focus": ["Protein-rich foods", "Healthy fats", "Whole grains", "Larger portions"],
                    "tips": "Eat calorie-dense, nutritious foods and consider adding healthy snacks between meals."
                },
                "diabetes_management": {
                    "title": "Diabetes Management",
                    "daily_calories": "1800-2200",
                    "focus": ["Low glycemic index foods", "High fiber", "Lean proteins", "Limited simple carbs"],
                    "tips": "Monitor carbohydrate intake and pair carbs with protein to manage blood sugar levels."
                }
            }
            
            return recommendations.get(goal_type, self._get_default_recommendations())
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return self._get_default_recommendations()
    
    def _get_default_recommendations(self) -> Dict:
        """Return default recommendations"""
        return {
            "title": "Healthy Balanced Diet",
            "daily_calories": "2000-2500",
            "focus": ["Variety from all food groups", "Fresh fruits and vegetables", "Whole grains", "Lean proteins"],
            "tips": "Eat a balanced diet with foods from all major food groups."
        }


# Global service instance
nutrition_service = NutritionService()

