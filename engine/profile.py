from lxml import html
import jmespath
import json
from engine.client import get_http_client

async def fetch_profile_data(username: str):
    url = f"https://www.tiktok.com/@{username}"
    client = get_http_client()
    response = await client.get(url)

    tree = html.fromstring(response.text)
    script = tree.xpath('//script[@id="__UNIVERSAL_DATA_FOR_REHYDRATION__"]/text()')
    if not script:
        return None

    try:
        raw_data = json.loads(script[0])
        profile = raw_data["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]
        return jmespath.search(
            """{
                id: user.id,
                uniqueId: user.uniqueId,
                nickname: user.nickname,
                avatar: user.avatarLarger,
                bio: user.signature,
                verified: user.verified,
                stats: stats
            }""",
            profile
        )
    except Exception:
        return None
