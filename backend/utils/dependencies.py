from typing import Optional
from fastapi import Depends, Header
from backend.services.auth_service import auth_service
from backend.utils.exceptions import AuthenticationError


async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """
    FastAPI dependency to extract and validate user from JWT token
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        User ID from validated token
        
    Raises:
        AuthenticationError: If token is missing or invalid
    """
    if not authorization:
        raise AuthenticationError("Missing authorization header")
    
    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid authorization header format")
    
    token = parts[1]
    
    # Verify token
    user_data = await auth_service.verify_token(token)
    if not user_data:
        raise AuthenticationError("Invalid or expired token")
    
    user_id = user_data.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")
    
    return user_id


async def get_current_user(user_id: str = Depends(get_current_user_id)) -> dict:
    """
    FastAPI dependency to get full user object
    
    Args:
        user_id: User ID from token (injected by get_current_user_id)
        
    Returns:
        Full user data dict
        
    Raises:
        AuthenticationError: If user not found
    """
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise AuthenticationError("User not found")
    
    return user

