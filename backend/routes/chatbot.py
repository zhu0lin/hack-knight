from fastapi import APIRouter, Depends, HTTPException
from schemas.chatbot_schemas import (
    ChatRequest,
    ChatResponse,
    QuickActionRequest,
    QuickActionResponse
)
from services.chatbot_service import chatbot_service
from utils.dependencies import get_current_user_id

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Send a message to the nutrition chatbot
    
    The chatbot will use the user's current nutrition data to provide
    personalized, context-aware responses.
    """
    try:
        response = await chatbot_service.chat(
            user_id=user_id,
            message=request.message,
            include_context=request.include_context
        )
        
        return ChatResponse(
            response=response,
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")


@router.get("/missing-groups", response_model=ChatResponse)
async def get_missing_food_groups(user_id: str = Depends(get_current_user_id)):
    """
    Quick action: Ask what food groups are missing today
    
    Example question: "What am I still missing today to fill in my food groups?"
    """
    try:
        response = await chatbot_service.get_missing_groups_explanation(user_id)
        
        return ChatResponse(
            response=response,
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")


@router.get("/meal-suggestions", response_model=ChatResponse)
async def get_meal_suggestions(user_id: str = Depends(get_current_user_id)):
    """
    Quick action: Get meal suggestions based on current nutrition
    
    The chatbot will suggest meals that fill in missing food groups
    """
    try:
        response = await chatbot_service.get_meal_suggestions(user_id)
        
        return ChatResponse(
            response=response,
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")


@router.get("/nutrition-tips", response_model=ChatResponse)
async def get_nutrition_tips(user_id: str = Depends(get_current_user_id)):
    """
    Quick action: Get personalized nutrition tips
    
    The chatbot will provide 3 quick tips based on eating patterns
    """
    try:
        response = await chatbot_service.get_nutrition_tips(user_id)
        
        return ChatResponse(
            response=response,
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")


@router.post("/quick-action", response_model=QuickActionResponse)
async def quick_action(
    request: QuickActionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Execute a quick chatbot action
    
    Available actions:
    - missing_groups: What food groups am I missing?
    - meal_suggestions: What should I eat next?
    - nutrition_tips: Give me nutrition tips
    """
    try:
        action_map = {
            "missing_groups": chatbot_service.get_missing_groups_explanation,
            "meal_suggestions": chatbot_service.get_meal_suggestions,
            "nutrition_tips": chatbot_service.get_nutrition_tips,
        }
        
        if request.action not in action_map:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action. Must be one of: {', '.join(action_map.keys())}"
            )
        
        action_func = action_map[request.action]
        response = await action_func(user_id)
        
        return QuickActionResponse(
            action=request.action,
            response=response,
            user_id=user_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")

