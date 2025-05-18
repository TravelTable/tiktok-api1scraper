from fastapi import APIRouter, Query, HTTPException
from engine.posts import fetch_user_posts
from engine.profile import fetch_profile_data
from engine.video import fetch_video_metadata
from engine.client import get_http_client

router = APIRouter()

@router.get("/posts")
async def get_user_posts(
    username: str = Query(..., description="TikTok username without @")
):
    try:
        posts = await fetch_user_posts(username)
        return {"success": True, "data": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_user_stats(
    username: str = Query(..., description="TikTok username without @")
):
    try:
        profile = await fetch_profile_data(username)
        if not profile or "stats" not in profile:
            raise HTTPException(status_code=404, detail="Stats not found")
        
        stats = profile["stats"]
        return {
            "success": True,
            "followers": stats.get("followerCount"),
            "likes": stats.get("heartCount"),
            "videos": stats.get("videoCount"),
            "avgViews": round(stats.get("playCount", 0) / max(stats.get("videoCount", 1), 1), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadata/raw")
async def get_raw_metadata(
    url: str = Query(..., description="Any TikTok user or video URL")
):
    try:
        client = get_http_client()
        response = await client.get(url)
        from lxml import html
        import json
        tree = html.fromstring(response.text)
        script = tree.xpath('//script[@id="__UNIVERSAL_DATA_FOR_REHYDRATION__"]/text()')
        if not script:
            raise HTTPException(status_code=404, detail="Metadata not found")
        raw = json.loads(script[0])
        return {"success": True, "data": raw}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
