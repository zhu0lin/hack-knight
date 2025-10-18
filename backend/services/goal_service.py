from typing import Dict, Optional, List
from datetime import datetime, date
from uuid import UUID
from services.supabase_client import get_supabase


class GoalService:
    """Service for user goal management and personalized recommendations"""
    
    def __init__(self):
        self.supabase = None
    
    def _get_supabase(self):
        """Lazy load Supabase client"""
        if self.supabase is None:
            self.supabase = get_supabase()
        return self.supabase
    
    async def create_or_update_goal(
        self,
        user_id: str,
        goal_type: str,
        target_calories: Optional[int] = None,
    ) -> Dict:
        """
        Create or update user's goal
        
        Args:
            user_id: User's UUID
            goal_type: Goal type (maintain, lose_weight, gain_weight, diabetes_management)
            target_calories: Optional target calories
            
        Returns:
            Created/updated goal data
        """
        try:
            # First, deactivate any existing active goals
            self._get_supabase().table("user_goals").update(
                {"is_active": False}
            ).eq("user_id", user_id).eq("is_active", True).execute()
            
            # Create new goal
            data = {
                "user_id": user_id,
                "goal_type": goal_type,
                "target_calories": target_calories,
                "is_active": True,
            }
            response = self._get_supabase().table("user_goals").insert(data).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating/updating goal: {e}")
            raise
    
    async def get_active_goal(self, user_id: str) -> Optional[Dict]:
        """
        Get user's active goal
        
        Args:
            user_id: User's UUID
            
        Returns:
            Active goal data or None
        """
        try:
            response = self._get_supabase().table("user_goals").select("*").eq(
                "user_id", user_id
            ).eq("is_active", True).order("created_at", desc=True).limit(1).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching active goal: {e}")
            return None
    
    async def get_nutrition_recommendations(self, goal_type: str) -> Dict:
        """
        Get personalized nutrition recommendations based on goal type
        
        Args:
            goal_type: Goal type (maintain, lose_weight, gain_weight, diabetes_management)
            
        Returns:
            Personalized nutrition recommendations
        """
        recommendations = {
            "lose_weight": {
                "title": "Weight Loss Plan",
                "daily_calories": "1,500-1,800 calories",
                "focus": [
                    "High protein intake (lean meats, fish, eggs)",
                    "Plenty of vegetables and leafy greens",
                    "Moderate fruits (2-3 servings)",
                    "Whole grains in small portions",
                    "Low-fat dairy products"
                ],
                "tips": "Focus on nutrient-dense, low-calorie foods. Prioritize vegetables and lean protein to stay full longer. Limit high-calorie foods and sugary drinks.",
                "macros": {
                    "protein": "30-35%",
                    "carbs": "35-40%",
                    "fat": "25-30%"
                },
                "priority_groups": ["vegetable", "protein", "fruit"],
                "calorie_modifier": -0.2  # 20% deficit
            },
            "gain_weight": {
                "title": "Weight Gain Plan",
                "daily_calories": "2,500-3,000 calories",
                "focus": [
                    "High protein foods (meats, eggs, protein shakes)",
                    "Complex carbohydrates (whole grains, rice, pasta)",
                    "Healthy fats (nuts, avocado, olive oil)",
                    "Full-fat dairy products",
                    "Frequent meals and snacks"
                ],
                "tips": "Eat calorie-dense foods and increase portion sizes. Add healthy fats to meals. Don't skip meals and consider protein shakes between meals.",
                "macros": {
                    "protein": "25-30%",
                    "carbs": "45-50%",
                    "fat": "25-30%"
                },
                "priority_groups": ["protein", "grain", "dairy"],
                "calorie_modifier": 0.2  # 20% surplus
            },
            "maintain": {
                "title": "Maintenance Plan",
                "daily_calories": "2,000-2,200 calories",
                "focus": [
                    "Balanced portions from all food groups",
                    "Variety of fruits and vegetables",
                    "Lean proteins and whole grains",
                    "Moderate dairy intake",
                    "Occasional treats in moderation"
                ],
                "tips": "Maintain a balanced diet with all food groups represented daily. Focus on consistency rather than restriction.",
                "macros": {
                    "protein": "20-25%",
                    "carbs": "45-50%",
                    "fat": "25-30%"
                },
                "priority_groups": ["vegetable", "fruit", "protein", "grain", "dairy"],
                "calorie_modifier": 0.0  # No change
            },
            "diabetes_management": {
                "title": "Diabetes Management Plan",
                "daily_calories": "1,800-2,200 calories",
                "focus": [
                    "Low glycemic index foods",
                    "High fiber vegetables",
                    "Lean proteins",
                    "Whole grains instead of refined",
                    "Limited fruits (focus on berries)"
                ],
                "tips": "Monitor carbohydrate intake carefully. Choose complex carbs over simple sugars. Eat regular meals to maintain stable blood sugar.",
                "macros": {
                    "protein": "25-30%",
                    "carbs": "40-45%",
                    "fat": "25-30%"
                },
                "priority_groups": ["vegetable", "protein", "grain"],
                "calorie_modifier": 0.0  # Depends on weight goal
            }
        }
        
        return recommendations.get(goal_type, recommendations["maintain"])
    
    async def get_personalized_advice(self, user_id: str, current_calories: int, food_groups_eaten: Dict[str, int]) -> str:
        """
        Generate personalized advice based on user's goal and current intake
        
        Args:
            user_id: User's UUID
            current_calories: Calories consumed today
            food_groups_eaten: Dictionary of food group counts
            
        Returns:
            Personalized advice string
        """
        try:
            goal = await self.get_active_goal(user_id)
            if not goal:
                return ""
            
            goal_type = goal.get("goal_type", "maintain")
            recommendations = await self.get_nutrition_recommendations(goal_type)
            
            priority_groups = recommendations.get("priority_groups", [])
            missing_priority = [g for g in priority_groups if food_groups_eaten.get(g, 0) == 0]
            
            # Build advice based on goal type
            advice_parts = []
            
            if goal_type == "lose_weight":
                if current_calories > 1800:
                    advice_parts.append("You're approaching your calorie target for weight loss.")
                if missing_priority:
                    advice_parts.append(f"For weight loss, prioritize {', '.join(missing_priority)}.")
            
            elif goal_type == "gain_weight":
                target_cals = goal.get("target_calories", 2500)
                if current_calories < target_cals * 0.6:
                    advice_parts.append(f"You need more calories to reach your gain goal ({target_cals} daily).")
                if "protein" in missing_priority or food_groups_eaten.get("protein", 0) < 3:
                    advice_parts.append("Add more protein to support muscle growth.")
            
            elif goal_type == "diabetes_management":
                if "grain" in food_groups_eaten and food_groups_eaten.get("grain", 0) > 2:
                    advice_parts.append("Monitor your carb intake. Choose whole grains over refined.")
                if "vegetable" in missing_priority:
                    advice_parts.append("Add more vegetables for fiber and blood sugar control.")
            
            return " ".join(advice_parts)
        except Exception as e:
            print(f"Error generating personalized advice: {e}")
            return ""
    
    async def calculate_target_calories(
        self,
        user_id: str,
        current_weight: Optional[float] = None,
        target_weight: Optional[float] = None,
        height: Optional[float] = None,
        age: Optional[int] = None,
        activity_level: str = "moderate"
    ) -> int:
        """
        Calculate target daily calories based on user data and goal
        
        Uses Harris-Benedict equation for BMR + activity multiplier
        
        Args:
            user_id: User's UUID
            current_weight: Weight in kg
            target_weight: Target weight in kg
            height: Height in cm
            age: Age in years
            activity_level: sedentary, light, moderate, active, very_active
            
        Returns:
            Recommended daily calories
        """
        try:
            goal = await self.get_active_goal(user_id)
            if not goal:
                return 2000  # Default maintenance
            
            # If all data is provided, calculate BMR
            if current_weight and height and age:
                # Using simplified Harris-Benedict equation (assuming average between male/female)
                bmr = 10 * current_weight + 6.25 * height - 5 * age + 5
                
                # Activity multipliers
                activity_multipliers = {
                    "sedentary": 1.2,
                    "light": 1.375,
                    "moderate": 1.55,
                    "active": 1.725,
                    "very_active": 1.9
                }
                
                maintenance_calories = int(bmr * activity_multipliers.get(activity_level, 1.55))
                
                # Apply goal modifier
                goal_type = goal.get("goal_type", "maintain")
                recommendations = await self.get_nutrition_recommendations(goal_type)
                modifier = recommendations.get("calorie_modifier", 0.0)
                
                target_calories = int(maintenance_calories * (1 + modifier))
                
                # Update goal with calculated calories if not set
                if not goal.get("target_calories"):
                    self._get_supabase().table("user_goals").update(
                        {"target_calories": target_calories}
                    ).eq("id", goal["id"]).execute()
                
                return target_calories
            else:
                # Use preset values based on goal type
                goal_type = goal.get("goal_type", "maintain")
                defaults = {
                    "lose_weight": 1650,
                    "gain_weight": 2750,
                    "maintain": 2100,
                    "diabetes_management": 2000
                }
                return defaults.get(goal_type, 2000)
        except Exception as e:
            print(f"Error calculating target calories: {e}")
            return 2000


# Global service instance
goal_service = GoalService()

