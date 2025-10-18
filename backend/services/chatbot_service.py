import google.generativeai as genai
from typing import Dict, List, Optional
from datetime import date
from config.settings import settings
from services.food_service import food_service
from services.nutrition_service import nutrition_service
from services.goal_service import goal_service


class ChatbotService:
    """Service for Gemini AI chatbot integration"""
    
    def __init__(self):
        # Configure Gemini API if key is provided
        self.model = None
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        else:
            print("Warning: GEMINI_API_KEY not configured, chatbot will return placeholder responses")
    
    async def get_user_context(self, user_id: str) -> str:
        """
        Gather user's nutrition context for chatbot
        
        Args:
            user_id: User's UUID
            
        Returns:
            Formatted context string
        """
        try:
            # Get today's food logs
            today_logs = await food_service.get_food_logs(
                user_id=user_id,
                start_date=date.today(),
                end_date=date.today(),
                limit=100
            )
            
            # Get missing food groups
            missing_groups = await nutrition_service.get_missing_food_groups(
                user_id=user_id,
                target_date=date.today()
            )
            
            # Get user's streak
            streak_info = await nutrition_service.calculate_streak(user_id)
            
            # Get user's goal
            user_goal = await goal_service.get_active_goal(user_id)
            
            # Count categories from today's meals
            category_counts = {
                'fruit': 0,
                'vegetable': 0,
                'protein': 0,
                'dairy': 0,
                'grain': 0,
            }
            
            total_calories = 0
            for log in today_logs:
                cat = log.get('food_category', '').lower()
                if cat in category_counts:
                    category_counts[cat] += 1
                total_calories += log.get('calories', 0)
            
            # Format context concisely
            context = f"""Today's nutrition data:
- Meals logged: {len(today_logs)}
- Categories: Fruits ({category_counts['fruit']}), Vegetables ({category_counts['vegetable']}), Protein ({category_counts['protein']}), Dairy ({category_counts['dairy']}), Grains ({category_counts['grain']})
- Total calories: {total_calories}
- Missing groups: {', '.join(missing_groups) if missing_groups else 'None'}
- Current streak: {streak_info.get('current_streak', 0)} days"""
            
            # Add goal information
            if user_goal:
                goal_type = user_goal.get('goal_type', 'maintain')
                target_cals = user_goal.get('target_calories')
                
                goal_names = {
                    'lose_weight': 'Weight Loss',
                    'gain_weight': 'Weight Gain',
                    'maintain': 'Maintenance',
                    'diabetes_management': 'Diabetes Management'
                }
                
                context += f"\n- Goal: {goal_names.get(goal_type, goal_type)}"
                if target_cals:
                    context += f"\n- Target calories: {target_cals}"
                    remaining = target_cals - total_calories
                    context += f"\n- Calories remaining: {remaining}"
                
                # Get personalized advice
                advice = await goal_service.get_personalized_advice(
                    user_id, total_calories, category_counts
                )
                if advice:
                    context += f"\n- Goal advice: {advice}"
            
            if today_logs:
                foods = [log.get('detected_food_name', 'Unknown') for log in today_logs[:5]]
                context += f"\n- Recent meals: {', '.join(foods)}"
            
            return context
        except Exception as e:
            print(f"Error gathering user context: {e}")
            return "Unable to retrieve nutrition data."
    
    async def chat(self, user_id: Optional[str], message: str, include_context: bool = True) -> str:
        """
        Send message to Gemini chatbot with optional user context
        
        Args:
            user_id: User's UUID (optional - if None, provides general advice)
            message: User's question/message
            include_context: Whether to include user's nutrition data (requires user_id)
            
        Returns:
            Chatbot response
        """
        try:
            # Check if Gemini is configured
            if not self.model:
                return "Chatbot is not configured. Please set GEMINI_API_KEY in your environment variables to enable the AI chatbot feature."
            
            # Build the prompt
            system_prompt = """You are a nutrition assistant for NutriBalance, a food tracking app. Provide short, concise, and actionable nutrition advice tailored to the user's weight goal.

Rules:
- Keep answers brief (2-4 sentences max)
- Be direct and specific
- Never use emojis
- Use bullet points only when listing multiple items
- Focus on practical advice
- Be encouraging but professional
- Personalize advice based on user's goal (weight loss, gain, maintenance, or diabetes management)
- For weight loss: emphasize high protein, vegetables, and staying within calorie targets
- For weight gain: emphasize calorie-dense foods, protein, and meeting calorie targets
- For diabetes: emphasize low glycemic foods and carb monitoring"""

            if include_context and user_id:
                user_context = await self.get_user_context(user_id)
                full_prompt = f"""{system_prompt}

{user_context}

User Question: {message}

Response:"""
            else:
                full_prompt = f"""{system_prompt}

User Question: {message}

Response:"""
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            return response.text
        except Exception as e:
            print(f"Error generating chatbot response: {e}")
            return "I'm having trouble processing your question right now. Please try again later."
    
    async def get_missing_groups_explanation(self, user_id: str) -> str:
        """
        Get explanation about missing food groups
        
        Args:
            user_id: User's UUID
            
        Returns:
            Chatbot explanation
        """
        question = "What food groups am I still missing today?"
        return await self.chat(user_id, question, include_context=True)
    
    async def get_meal_suggestions(self, user_id: str) -> str:
        """
        Get meal suggestions based on missing food groups
        
        Args:
            user_id: User's UUID
            
        Returns:
            Meal suggestions
        """
        question = "Based on what I've eaten, what should I eat next?"
        return await self.chat(user_id, question, include_context=True)
    
    async def get_nutrition_tips(self, user_id: str) -> str:
        """
        Get personalized nutrition tips
        
        Args:
            user_id: User's UUID
            
        Returns:
            Nutrition tips
        """
        question = "Give me 2-3 quick tips based on my eating today."
        return await self.chat(user_id, question, include_context=True)


# Global service instance
chatbot_service = ChatbotService()

