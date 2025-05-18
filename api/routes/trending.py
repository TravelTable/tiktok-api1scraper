from fastapi import APIRouter, Query, HTTPException
from engine.trending import fetch_trending_videos

router = APIRouter()

@router.get("")
async def get_trending_videos(region: str = Query("US", description="Region code (e.g., US, AU, IN)")):
    try:
        results = await fetch_trending_videos(region)
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
