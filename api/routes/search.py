from fastapi import APIRouter, Query, HTTPException
from engine.search import fetch_search_results

router = APIRouter()

@router.get("")
async def search_tiktok(
    keyword: str = Query(..., description="Search term"),
    limit: int = Query(12, description="Number of results to return")
):
    try:
        results = await fetch_search_results(keyword, limit=limit)
        return {"success": True, "count": len(results), "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
