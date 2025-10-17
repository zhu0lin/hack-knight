from typing import Optional, Dict
from jose import jwt, JWTError
from backend.config.settings import settings
from backend.services.supabase_client import get_supabase


class AuthService:
    """Authentication service for handling Supabase auth operations"""
    
    def __init__(self):
        self.supabase = get_supabase()
    
    async def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify Supabase JWT token and return user data
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            User data dict if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated"
            )
            return payload
        except JWTError:
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Get user data from Supabase by user ID
        
        Args:
            user_id: User's UUID
            
        Returns:
            User data dict if found
        """
        try:
            response = self.supabase.table("users").select("*").eq("id", user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    
    async def create_user_profile(self, user_id: str, email: str, full_name: Optional[str] = None) -> Dict:
        """
        Create user profile on first signup
        
        Args:
            user_id: User's UUID from Supabase auth
            email: User's email
            full_name: Optional full name
            
        Returns:
            Created user profile data
        """
        try:
            data = {
                "id": user_id,
                "full_name": full_name,
            }
            response = self.supabase.table("users").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating user profile: {e}")
            raise


# Global service instance
auth_service = AuthService()

