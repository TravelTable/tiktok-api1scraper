from fastapi import APIRouter, Query, HTTPException
from engine.hashtag import fetch_hashtag_data

router = APIRouter()

@router.get("")
async def get_hashtag_data(
    name: str = Query(..., description="Hashtag name without #")
):
    try:
        result = await fetch_hashtag_data(name)
        if not result:
            raise HTTPException(status_code=404, detail="Hashtag not found")
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
