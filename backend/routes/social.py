from fastapi import APIRouter

router = APIRouter(prefix="/api/social", tags=["Social"])


@router.get("/friends")
async def get_friends():
    """Get friends list"""
    return {"message": "Get friends endpoint - to be implemented (future feature)"}


@router.post("/friends")
async def add_friend():
    """Add friend"""
    return {"message": "Add friend endpoint - to be implemented (future feature)"}


@router.get("/leaderboard")
async def get_leaderboard():
    """Get friends streak leaderboard"""
    return {"message": "Leaderboard endpoint - to be implemented (future feature)"}

