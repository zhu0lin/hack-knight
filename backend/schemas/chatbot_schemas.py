from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    """Schema for chatbot message request"""
    message: str
    include_context: bool = True


class ChatResponse(BaseModel):
    """Schema for chatbot response"""
    response: str
    user_id: str


class QuickActionRequest(BaseModel):
    """Schema for quick action requests (no message needed)"""
    action: str  # 'missing_groups', 'meal_suggestions', 'nutrition_tips'


class QuickActionResponse(BaseModel):
    """Schema for quick action response"""
    action: str
    response: str
    user_id: str

