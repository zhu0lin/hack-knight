from typing import List, Optional, Dict
from datetime import datetime, date
from uuid import UUID
from services.supabase_client import get_supabase


class FoodService:
    """Service for food logging business logic"""
    
    def __init__(self):
        self.supabase = None
    
    def _get_supabase(self):
        """Lazy load Supabase client"""
        if self.supabase is None:
            self.supabase = get_supabase()
        return self.supabase
    
    async def create_food_log(
        self,
        user_id: Optional[str],
        image_url: str,
        detected_food_name: str,
        food_category: str,
        healthiness_score: int,
        calories: Optional[int] = None,
        meal_type: Optional[str] = None,
    ) -> Dict:
        """
        Create a new food log entry
        
        Args:
            user_id: User's UUID (optional, None for anonymous users)
            image_url: URL to uploaded food image
            detected_food_name: Name detected by ML model
            food_category: Category (fruit, vegetable, etc)
            healthiness_score: Score from 0-100
            calories: Optional calorie count
            meal_type: Optional meal type
            
        Returns:
            Created food log data
        """
        try:
            data = {
                "user_id": user_id,
                "image_url": image_url,
                "detected_food_name": detected_food_name,
                "food_category": food_category,
                "healthiness_score": healthiness_score,
                "calories": calories,
                "meal_type": meal_type,
                "logged_at": datetime.utcnow().isoformat(),
            }
            response = self._get_supabase().table("food_logs").insert(data).execute()
            
            # Update daily summary after creating log (only for authenticated users)
            if response.data and user_id:
                await self.update_daily_summary(user_id, date.today())
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating food log: {e}")
            raise
    
    async def get_food_logs(
        self,
        user_id: str,
        limit: int = 50,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict]:
        """
        Get user's food logs with optional filters
        
        Args:
            user_id: User's UUID
            limit: Maximum number of logs to return
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of food log entries
        """
        try:
            query = self._get_supabase().table("food_logs").select("*").eq("user_id", user_id).order("logged_at", desc=True).limit(limit)
            
            if start_date:
                query = query.gte("logged_at", start_date.isoformat())
            if end_date:
                query = query.lte("logged_at", end_date.isoformat())
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching food logs: {e}")
            return []
    
    async def get_all_food_logs(
        self,
        limit: int = 100,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict]:
        """
        Get all food logs from all users with optional filters
        
        Args:
            limit: Maximum number of logs to return
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of food log entries from all users
        """
        try:
            query = self._get_supabase().table("food_logs").select("*").order("logged_at", desc=True).limit(limit)
            
            if start_date:
                query = query.gte("logged_at", start_date.isoformat())
            if end_date:
                query = query.lte("logged_at", end_date.isoformat())
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching all food logs: {e}")
            return []
    
    async def update_daily_summary(self, user_id: str, summary_date: date) -> None:
        """
        Update or create daily nutrition summary for a user
        
        Args:
            user_id: User's UUID
            summary_date: Date to calculate summary for
        """
        try:
            # Get all food logs for the day
            logs = await self.get_food_logs(
                user_id,
                start_date=summary_date,
                end_date=summary_date,
            )
            
            # Calculate counts by category
            category_counts = {
                "fruits_count": 0,
                "vegetables_count": 0,
                "protein_count": 0,
                "dairy_count": 0,
                "grains_count": 0,
                "total_calories": 0,
            }
            
            for log in logs:
                category = log.get("food_category")
                if category == "fruit":
                    category_counts["fruits_count"] += 1
                elif category == "vegetable":
                    category_counts["vegetables_count"] += 1
                elif category == "protein":
                    category_counts["protein_count"] += 1
                elif category == "dairy":
                    category_counts["dairy_count"] += 1
                elif category == "grain":
                    category_counts["grains_count"] += 1
                
                if log.get("calories"):
                    category_counts["total_calories"] += log["calories"]
            
            # Calculate completion percentage (each category = 20%)
            completion = sum([
                20 if category_counts["fruits_count"] > 0 else 0,
                20 if category_counts["vegetables_count"] > 0 else 0,
                20 if category_counts["protein_count"] > 0 else 0,
                20 if category_counts["dairy_count"] > 0 else 0,
                20 if category_counts["grains_count"] > 0 else 0,
            ])
            
            # Upsert daily summary
            data = {
                "user_id": user_id,
                "date": summary_date.isoformat(),
                **category_counts,
                "completion_percentage": completion,
            }
            
            self._get_supabase().table("daily_nutrition_summary").upsert(data).execute()
        except Exception as e:
            print(f"Error updating daily summary: {e}")


# Global service instance
food_service = FoodService()

