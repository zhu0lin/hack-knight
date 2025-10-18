from fastapi import APIRouter

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup")
async def signup():
    """Create account with Supabase OAuth"""
    return {"message": "Signup endpoint - to be implemented"}


@router.post("/login")
async def login():
    """Login with OAuth provider"""
    return {"message": "Login endpoint - to be implemented"}


@router.post("/logout")
async def logout():
    """Logout user"""
    return {"message": "Logout endpoint - to be implemented"}


@router.get("/me")
async def get_current_user():
    """Get current user info"""
    return {"message": "Get current user endpoint - to be implemented"}

