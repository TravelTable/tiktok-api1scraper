from fastapi import APIRouter, Query, HTTPException
from engine.comments import fetch_video_comments

router = APIRouter()

@router.get("")
async def get_comments(
    url: str = Query(..., description="TikTok video URL"),
    limit: int = Query(20, description="Number of comments per page"),
    cursor: int = Query(0, description="Pagination cursor (offset)")
):
    try:
        data = await fetch_video_comments(url, limit=limit, cursor=cursor)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
