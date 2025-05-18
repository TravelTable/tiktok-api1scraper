import subprocess
import json
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

@router.get("/comments-browser")
async def scrape_tiktok_comments(
    url: str = Query(..., description="Full TikTok video URL"),
    max: int = Query(50, description="Max number of comments to scrape")
):
    try:
        result = subprocess.run(
            ["node", "./node/scrapeComments.js", url, str(max)],
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8"
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Scraping process timed out.")

    if not result.stdout:
        raise HTTPException(status_code=500, detail=f"""
Scraper returned no output.

STDOUT:
{result.stdout}

STDERR:
{result.stderr}
""")

    try:
        # 🔥 Fix: Strip only the actual JSON (start with '{' and end with '}')
        lines = result.stdout.splitlines()
        json_block = None
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_str = "\n".join(lines[i:])
                try:
                    json_block = json.loads(json_str)
                    break
                except json.JSONDecodeError:
                    continue

        if json_block is None:
            raise ValueError("No valid JSON found in output.")

        return json_block

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON from scraper:\n{result.stdout}\n\nError: {e}")
