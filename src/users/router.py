"""
User management router (placeholder)
TODO: Implement full user management endpoints
"""
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def get_users():
    """Get users (placeholder)"""
    return {"message": "Users endpoint - TODO: Implement"}
