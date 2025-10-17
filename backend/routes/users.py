from fastapi import APIRouter

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/profile")
async def get_user_profile():
    """Get user profile"""
    return {"message": "Get profile endpoint - to be implemented"}


@router.put("/profile")
async def update_user_profile():
    """Update profile (weight, height, etc)"""
    return {"message": "Update profile endpoint - to be implemented"}


@router.post("/onboarding")
async def complete_onboarding():
    """Complete initial setup (goals, preferences)"""
    return {"message": "Onboarding endpoint - to be implemented"}

