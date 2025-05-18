from fastapi import APIRouter, Query, HTTPException
from engine.profile import fetch_profile_data

router = APIRouter()

@router.get("")
async def get_profile(
    username: str = Query(..., description="TikTok username without @")
):
    try:
        data = await fetch_profile_data(username)
        if not data:
            raise HTTPException(status_code=404, detail="Profile not found or invalid")
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
