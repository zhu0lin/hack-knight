import google.generativeai as genai
from typing import Dict, List, Optional
from datetime import date
from config.settings import settings
from services.food_service import food_service
from services.nutrition_service import nutrition_service


class ChatbotService:
    """Service for Gemini AI chatbot integration"""
    
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
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
            
            # Format context
            context = f"""
User's Nutrition Data for Today:

Food Logs ({len(today_logs)} items):
"""
            
            if today_logs:
                for log in today_logs:
                    context += f"- {log.get('detected_food_name', 'Unknown')} ({log.get('food_category', 'unknown')} category, {log.get('healthiness_score', 0)} health score, {log.get('calories', 0)} calories)\n"
            else:
                context += "- No food logged yet today\n"
            
            context += f"\nMissing Food Groups: {', '.join(missing_groups) if missing_groups else 'None - all groups completed!'}\n"
            context += f"\nCurrent Streak: {streak_info.get('current_streak', 0)} days\n"
            context += f"Longest Streak: {streak_info.get('longest_streak', 0)} days\n"
            
            return context
        except Exception as e:
            print(f"Error gathering user context: {e}")
            return "Unable to retrieve user nutrition data at this time."
    
    async def chat(self, user_id: str, message: str, include_context: bool = True) -> str:
        """
        Send message to Gemini chatbot with optional user context
        
        Args:
            user_id: User's UUID
            message: User's question/message
            include_context: Whether to include user's nutrition data
            
        Returns:
            Chatbot response
        """
        try:
            # Build the prompt
            system_prompt = """You are a helpful nutrition assistant for a food tracking app called Food App. 
Your role is to help users understand their nutrition, answer questions about their food intake, 
and provide encouraging, scientifically-accurate nutrition advice.

Key responsibilities:
- Answer questions about their daily nutrition progress
- Explain what food groups they're missing
- Provide suggestions for balanced meals
- Encourage healthy eating habits
- Explain nutrition concepts simply

Keep responses concise, friendly, and actionable. Use emojis occasionally to be engaging."""

            if include_context:
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
        Get detailed explanation about missing food groups
        
        Args:
            user_id: User's UUID
            
        Returns:
            Chatbot explanation
        """
        question = "What food groups am I still missing today to have a complete balanced diet?"
        return await self.chat(user_id, question, include_context=True)
    
    async def get_meal_suggestions(self, user_id: str) -> str:
        """
        Get meal suggestions based on missing food groups
        
        Args:
            user_id: User's UUID
            
        Returns:
            Meal suggestions
        """
        question = "Based on what I've eaten today, what should I eat next to balance my nutrition?"
        return await self.chat(user_id, question, include_context=True)
    
    async def get_nutrition_tips(self, user_id: str) -> str:
        """
        Get personalized nutrition tips
        
        Args:
            user_id: User's UUID
            
        Returns:
            Nutrition tips
        """
        question = "Give me 3 quick nutrition tips based on my eating pattern today."
        return await self.chat(user_id, question, include_context=True)


# Global service instance
chatbot_service = ChatbotService()

