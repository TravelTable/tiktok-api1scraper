from engine.client import get_http_client
import json
import jmespath

async def fetch_user_posts(username: str):
    url = f"https://www.tiktok.com/@{username}"
    client = get_http_client()
    response = await client.get(url)

    if response.status_code != 200:
        return None

    try:
        from lxml import html
        tree = html.fromstring(response.text)
        script = tree.xpath('//script[@id="__UNIVERSAL_DATA_FOR_REHYDRATION__"]/text()')
        if not script:
            return None

        data = json.loads(script[0])
        items = data["__DEFAULT_SCOPE__"]["webapp.user-detail"]["itemList"]
        return [
            jmespath.search(
                """{
                    id: id,
                    desc: desc,
                    createTime: createTime,
                    stats: stats,
                    video: video.{duration: duration, playAddr: playAddr, downloadAddr: downloadAddr, cover: cover}
                }""",
                item,
            )
            for item in items
        ]
    except Exception:
        return None
