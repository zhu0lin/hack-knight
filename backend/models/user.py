from typing import Optional
from datetime import datetime
from uuid import UUID


class User:
    """User data model representing users table in Supabase"""
    
    def __init__(
        self,
        id: UUID,
        created_at: datetime,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        current_weight: Optional[float] = None,
        target_weight: Optional[float] = None,
        height: Optional[float] = None,
        age: Optional[int] = None,
    ):
        self.id = id
        self.created_at = created_at
        self.full_name = full_name
        self.avatar_url = avatar_url
        self.current_weight = current_weight
        self.target_weight = target_weight
        self.height = height
        self.age = age

