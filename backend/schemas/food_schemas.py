from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class FoodLogBase(BaseModel):
    """Base food log schema"""
    detected_food_name: str
    food_category: str  # 'fruit', 'vegetable', 'protein', 'dairy', 'grain', 'other'
    healthiness_score: int  # 0-100
    calories: Optional[int] = None
    meal_type: Optional[str] = None  # 'breakfast', 'lunch', 'dinner', 'snack'


class FoodLogCreate(BaseModel):
    """Schema for creating a food log"""
    meal_type: Optional[str] = None


class FoodUploadRequest(BaseModel):
    """Schema for uploading food image"""
    image_base64: str
    meal_type: Optional[str] = None


class FoodUploadResponse(BaseModel):
    """Response after uploading and analyzing food image"""
    log_id: UUID
    image_url: str
    detected_food_name: str
    food_category: str
    healthiness_score: int
    calories: Optional[int]
    meal_type: Optional[str]
    confidence: Optional[float]
    message: str


class FoodLogResponse(FoodLogBase):
    """Complete food log response"""
    id: UUID
    user_id: UUID
    image_url: str
    logged_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class FoodLogUpdate(BaseModel):
    """Schema for updating a food log"""
    detected_food_name: Optional[str] = None
    food_category: Optional[str] = None
    healthiness_score: Optional[int] = None
    calories: Optional[int] = None
    meal_type: Optional[str] = None


class FoodLogsListResponse(BaseModel):
    """Response for list of food logs"""
    logs: list[FoodLogResponse]
    total: int
    page: int
    limit: int


class MLAnalysisResult(BaseModel):
    """Schema for ML model analysis result"""
    food_name: str
    category: str
    healthiness_score: int
    calories: int
    confidence: Optional[float] = None

