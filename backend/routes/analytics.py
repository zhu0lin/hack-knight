from fastapi import APIRouter

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/today")
async def get_today_summary():
    """Get today's nutrition summary"""
    return {"message": "Today's summary endpoint - to be implemented"}


@router.get("/week")
async def get_week_summary():
    """Get weekly nutrition summary"""
    return {"message": "Weekly summary endpoint - to be implemented"}


@router.get("/missing")
async def get_missing_food_groups():
    """Get what food groups are missing today"""
    return {"message": "Missing food groups endpoint - to be implemented"}


@router.get("/streak")
async def get_user_streak():
    """Get user's current streak"""
    return {"message": "User streak endpoint - to be implemented"}

