from engine.client import get_http_client
import jmespath

async def fetch_trending_videos(region: str = "US"):
    url = f"https://www.tiktok.com/trending?region={region.upper()}"
    client = get_http_client()
    response = await client.get(url)
    
    from lxml import html
    import json

    tree = html.fromstring(response.text)
    script = tree.xpath('//script[@id="__UNIVERSAL_DATA_FOR_REHYDRATION__"]/text()')
    if not script:
        return []

    data = json.loads(script[0])
    items = data["__DEFAULT_SCOPE__"].get("webapp.trending", {}).get("itemList", [])

    return [
        jmespath.search(
            """{
                id: id,
                desc: desc,
                author: author.{uniqueId: uniqueId, nickname: nickname},
                stats: stats,
                video: video.{playAddr: playAddr, cover: cover}
            }""",
            item,
        )
        for item in items
    ]
