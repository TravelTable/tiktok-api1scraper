from fastapi import APIRouter, Query, HTTPException
from engine.posts import fetch_user_posts

router = APIRouter()

@router.get("")
async def get_channel_posts(
    username: str = Query(..., description="TikTok username without @")
):
    try:
        data = await fetch_user_posts(username)
        if not data:
            raise HTTPException(status_code=404, detail="No videos found")
        return {"success": True, "count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
