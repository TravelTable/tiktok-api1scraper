import re
import json
from urllib.parse import urlencode, urlparse
from lxml import html
from engine.client import get_http_client

def extract_video_id(url: str) -> str:
    match = re.search(r"/video/(\d+)", url)
    return match.group(1) if match else None

async def fetch_video_comments(url: str, limit=20, cursor=0):
    client = get_http_client()
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError("Invalid video URL")

    api_url = "https://www.tiktok.com/api/comment/list/?" + urlencode({
        "aweme_id": video_id,
        "count": limit,
        "cursor": cursor
    })

    headers = client.headers.copy()
    headers["referer"] = url

    response = await client.get(api_url, headers=headers)
    raw = response.json()

    return {
        "comments": raw.get("comments", []),
        "total": raw.get("total", 0),
        "has_more": raw.get("has_more", 0),
        "next_cursor": raw.get("cursor", 0)
    }
