from engine.client import get_http_client
import json
import jmespath
from lxml import html

async def fetch_hashtag_data(tag: str):
    url = f"https://www.tiktok.com/tag/{tag}"
    client = get_http_client()
    response = await client.get(url)

    if response.status_code != 200:
        return None

    tree = html.fromstring(response.text)
    script = tree.xpath('//script[@id="__UNIVERSAL_DATA_FOR_REHYDRATION__"]/text()')
    if not script:
        return None

    try:
        data = json.loads(script[0])
        hashtag_data = data["__DEFAULT_SCOPE__"]["webapp.challenge-detail"]["challengeInfo"]

        return jmespath.search(
            """{
                id: challenge.id,
                title: challenge.title,
                desc: challenge.desc,
                cover: challenge.coverLarger,
                stats: stats
            }""",
            hashtag_data
        )
    except Exception:
        return None
