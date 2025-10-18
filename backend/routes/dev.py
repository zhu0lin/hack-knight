from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
from config.settings import settings

router = APIRouter(prefix="/api/dev", tags=["Development"])


class TestUserRequest(BaseModel):
    """Request to create a test JWT token"""
    user_id: str = "test-user-123"
    email: str = "test@example.com"
    expires_in_hours: int = 24


class TestTokenResponse(BaseModel):
    """Response with test JWT token"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    expires_at: str
    instructions: str


@router.post("/generate-test-token", response_model=TestTokenResponse)
async def generate_test_token(request: TestUserRequest):
    """
    Generate a test JWT token for development/testing
    
    ⚠️ THIS IS FOR DEVELOPMENT ONLY - DO NOT USE IN PRODUCTION
    
    Creates a JWT token that mimics what Supabase would generate.
    Use this token in the Authorization header: Bearer <token>
    """
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=403,
            detail="Test token generation is disabled in production"
        )
    
    try:
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(hours=request.expires_in_hours)
        
        # Create JWT payload (mimicking Supabase JWT structure)
        payload = {
            "sub": request.user_id,  # Subject (user ID)
            "email": request.email,
            "aud": "authenticated",
            "role": "authenticated",
            "iat": int(datetime.utcnow().timestamp()),  # Issued at
            "exp": int(expires_at.timestamp()),  # Expiration
        }
        
        # Sign the token with your Supabase JWT secret
        token = jwt.encode(
            payload,
            settings.SUPABASE_JWT_SECRET,
            algorithm="HS256"
        )
        
        instructions = f"""
🔑 Test Token Generated Successfully!

How to use this token:

1. In Swagger UI (http://localhost:8000/docs):
   - Click the 🔒 Authorize button
   - Enter: Bearer {token[:30]}...
   - Click Authorize

2. In cURL:
   curl -H "Authorization: Bearer {token}" \\
        http://localhost:8000/api/chatbot/missing-groups

3. In your frontend:
   headers: {{
     'Authorization': 'Bearer {token[:30]}...'
   }}

Token expires at: {expires_at.isoformat()}
User ID: {request.user_id}
"""
        
        return TestTokenResponse(
            access_token=token,
            user_id=request.user_id,
            expires_at=expires_at.isoformat(),
            instructions=instructions
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate test token: {str(e)}"
        )


@router.get("/test-auth")
async def test_auth_endpoint():
    """
    Test endpoint that doesn't require authentication
    
    Use this to verify the API is running before testing protected endpoints.
    """
    return {
        "message": "✅ API is running!",
        "environment": settings.ENVIRONMENT,
        "instructions": [
            "1. Generate a test token at POST /api/dev/generate-test-token",
            "2. Use the token to access protected endpoints",
            "3. Visit /docs to see all available endpoints"
        ],
        "protected_endpoints": [
            "POST /api/chatbot/chat",
            "GET /api/chatbot/missing-groups",
            "GET /api/chatbot/meal-suggestions",
            "GET /api/analytics/today"
        ]
    }

