from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from supabase import create_client, Client
import google.generativeai as genai
import os
from typing import Optional, Dict, List, Set
from collections import defaultdict

app = FastAPI(
    title="Hack Knight API",
    description="Backend API for Hack Knight application",
    version="1.0.0"
)

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Optional[Client] = None

if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)

# Initialize Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Hack Knight API! 🏰",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/api/hello")
async def hello():
    """Sample API endpoint"""
    return {
        "message": "Hello from FastAPI!",
        "description": "This is a sample endpoint to demonstrate the API structure"
    }

ALL_FOOD_GROUPS = {
    "fruit",
    "vegetable",
    "grain",
    "protein",
    "dairy"
}

FOOD_GROUP_ALIASES: Dict[str, str] = {
    "fruit": "fruit",
    "fruits": "fruit",
    "vegetable": "vegetable",
    "vegetables": "vegetable",
    "grain": "grain",
    "grains": "grain",
    "protein": "protein",
    "proteins": "protein",
    "dairy": "dairy",
    "milk": "dairy",
    "healthy fat": "healthy_fats",
    "healthy fats": "healthy_fats",
    "fat": "healthy_fats",
    "fats": "healthy_fats",
}


class ChatRequest(BaseModel):
    user_id: str
    message: str


def _parse_logged_date(logged_at: Optional[str]) -> Optional[date]:
    """Best-effort parser for Supabase timestamp strings."""
    if not logged_at:
        return None
    try:
        return datetime.fromisoformat(logged_at.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(logged_at[:10])
        except ValueError:
            return None


def _normalize_category(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    key = name.strip().lower()
    return FOOD_GROUP_ALIASES.get(key)


def _calculate_consecutive_streak(completed_days: List[date], today: date) -> int:
    if not completed_days:
        return 0

    completed_days_sorted = sorted(set(completed_days), reverse=True)
    most_recent = completed_days_sorted[0]
    days_since_last = (today - most_recent).days

    if days_since_last > 1:
        return 0

    streak = 1
    previous = most_recent

    for day in completed_days_sorted[1:]:
        if (previous - day).days == 1:
            streak += 1
            previous = day
        else:
            break

    return streak

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat endpoint that uses Gemini AI with user context"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    if not gemini_model:
        raise HTTPException(status_code=500, detail="Gemini API not configured")
    
    try:
        # Fetch user goal
        user_goal_response = supabase.table("user_goals")\
            .select("goal_type")\
            .eq("user_id", request.user_id)\
            .eq("is_active", True)\
            .single()\
            .execute()
        
        user_goal = user_goal_response.data.get("goal_type", "maintain") if user_goal_response.data else "maintain"
        
        # Fetch user profile
        user_profile_response = supabase.table("users")\
            .select("full_name, age, current_weight, target_weight, height")\
            .eq("id", request.user_id)\
            .single()\
            .execute()
        
        user_profile = user_profile_response.data if user_profile_response.data else {}
        
        # Fetch recent food logs (last 7 days)
        today = date.today()
        seven_days_ago = today - timedelta(days=7)
        recent_foods_response = supabase.table("food_logs")\
            .select("detected_food_name, food_category, healthiness_score, calories, meal_type, logged_at")\
            .eq("user_id", request.user_id)\
            .gte("logged_at", seven_days_ago.isoformat())\
            .order("logged_at", desc=True)\
            .execute()
        
        recent_foods = recent_foods_response.data if recent_foods_response.data else []
        
        # Calculate today's food categories
        today_foods = [
            food for food in recent_foods 
            if food['logged_at'] and food['logged_at'].startswith(today.isoformat())
        ]
        today_categories = set(food['food_category'] for food in today_foods if food.get('food_category'))
        all_categories = {'fruit', 'vegetable', 'protein', 'dairy', 'grain'}
        missing_categories = all_categories - today_categories
        
        # Format food logs for prompt
        food_log_text = "\n".join([
            f"- {food['detected_food_name']} ({food['food_category']}, {food.get('calories', 'N/A')} cal, healthiness: {food['healthiness_score']}/100)"
            for food in recent_foods[:10]  # Limit to last 10 meals
        ]) if recent_foods else "No recent meals logged"
        
        # Build system prompt
        system_prompt = f"""You are a nutrition assistant for NutriBalance app.

User Profile:
- Goal: {user_goal}
- Age: {user_profile.get('age', 'N/A')}
- Current weight: {user_profile.get('current_weight', 'N/A')} kg
- Target weight: {user_profile.get('target_weight', 'N/A')} kg
- Height: {user_profile.get('height', 'N/A')} cm

Recent meals (last 7 days):
{food_log_text}

Today's food groups consumed: {', '.join(today_categories) if today_categories else 'None yet'}
Today's missing food groups: {', '.join(missing_categories) if missing_categories else 'All groups covered!'}

Provide helpful, personalized, and concise nutrition advice. Be friendly and encouraging."""

        # Call Gemini
        full_prompt = f"{system_prompt}\n\nUser: {request.message}\n\nAssistant:"
        response = gemini_model.generate_content(full_prompt)
        
        return {
            "response": response.text,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.get("/api/users/{user_id}/streak")
async def get_user_streak(user_id: str):
    """Compute the user's current streak based on completed food groups."""
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    try:
        response = supabase.table("food_logs")\
            .select("food_category, logged_at")\
            .eq("user_id", user_id)\
            .order("logged_at", desc=True)\
            .limit(500)\
            .execute()

        logs: List[Dict[str, str]] = response.data if response.data else []

        daily_groups: Dict[date, Set[str]] = defaultdict(set)

        for entry in logs:
            group = _normalize_category(entry.get("food_category"))
            logged_date = _parse_logged_date(entry.get("logged_at"))

            if not group or not logged_date:
                continue

            daily_groups[logged_date].add(group)

        completed_days = [
            day for day, groups in daily_groups.items()
            if ALL_FOOD_GROUPS.issubset(groups)
        ]

        today = date.today()
        current_streak = _calculate_consecutive_streak(completed_days, today)
        last_completed_date = max(completed_days).isoformat() if completed_days else None

        return {
            "current_streak": current_streak,
            "last_completed_date": last_completed_date,
            "completed_days": sorted([day.isoformat() for day in completed_days], reverse=True)
        }
    except Exception as exc:
        print(f"Streak error: {exc}")
        raise HTTPException(status_code=500, detail="Error calculating streak")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
