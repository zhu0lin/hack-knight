from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    current_weight: Optional[float] = None
    target_weight: Optional[float] = None
    height: Optional[float] = None
    age: Optional[int] = None


class UserProfileResponse(UserBase):
    """User profile response schema"""
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    current_weight: Optional[float] = None
    target_weight: Optional[float] = None
    height: Optional[float] = None
    age: Optional[int] = None


class OnboardingRequest(BaseModel):
    """Schema for initial user onboarding"""
    full_name: str
    age: Optional[int] = None
    height: Optional[float] = None
    current_weight: Optional[float] = None
    target_weight: Optional[float] = None
    goal_type: str  # 'maintain', 'lose_weight', 'gain_weight', 'diabetes_management'
    target_calories: Optional[int] = None


class OnboardingResponse(BaseModel):
    """Response after completing onboarding"""
    user: UserProfileResponse
    goal_id: UUID
    message: str

