from engine.client import get_http_client
import json
import jmespath
from urllib.parse import quote

async def fetch_search_results(keyword: str, limit: int = 12):
    client = get_http_client()
    encoded = quote(keyword)
    url = f"https://www.tiktok.com/api/search/general/full/?keyword={encoded}&offset=0&count={limit}"
    headers = {
        "referer": f"https://www.tiktok.com/search?q={encoded}"
    }

    response = await client.get(url, headers=headers)
    data = response.json()
    results = []

    for item in data.get("data", []):
        if item.get("type") != 1 or "item" not in item:
            continue

        parsed = jmespath.search(
            """{
                id: item.id,
                desc: item.desc,
                author: item.author.{nickname: nickname, uniqueId: uniqueId},
                stats: item.stats,
                video: item.video.{duration: duration, cover: cover, playAddr: playAddr}
            }""",
            item
        )
        results.append(parsed)

    return results
