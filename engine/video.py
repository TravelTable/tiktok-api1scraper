from engine.client import get_http_client
from lxml import html
import jmespath
import json
from loguru import logger

async def fetch_video_metadata(url: str):
    logger.debug(f"[video] Fetching TikTok video page: {url}")
    client = get_http_client()
    try:
        response = await client.get(url)
    except Exception as e:
        logger.exception(f"[video] HTTP request failed: {e}")
        return None

    logger.debug(f"[video] Response status: {response.status_code}")
    if response.status_code != 200:
        logger.error("[video] Non-200 status code received")
        return None

    try:
        tree = html.fromstring(response.text)
        logger.debug("[video] Parsed HTML tree")

        script = tree.xpath('//script[@id="__UNIVERSAL_DATA_FOR_REHYDRATION__"]/text()')
        logger.debug(f"[video] Extracted script tags: {bool(script)}")

        if not script:
            logger.error("[video] Script tag not found in page")
            return None

        raw_json = script[0]
        logger.debug(f"[video] Extracted JSON string length: {len(raw_json)}")

        data = json.loads(raw_json)
        logger.debug("[video] JSON parsed successfully")

        scope = data.get("__DEFAULT_SCOPE__", {})
        video_data = scope.get("webapp.video-detail", {}).get("itemInfo", {}).get("itemStruct")

        if not video_data:
            logger.error("[video] itemStruct not found in metadata")
            return None

        parsed = jmespath.search(
            """{
                id: id,
                desc: desc,
                createTime: createTime,
                video: video.{duration: duration, ratio: ratio, cover: cover, playAddr: playAddr, downloadAddr: downloadAddr},
                author: author.{uniqueId: uniqueId, nickname: nickname},
                stats: stats
            }""",
            video_data
        )
        logger.debug(f"[video] Final parsed video metadata: {parsed}")
        return parsed

    except Exception as e:
        logger.exception(f"[video] Full error during metadata extraction: {e}")
        return None


async def fetch_video_download_url(url: str):
    logger.debug(f"[video] Fetching download URL for: {url}")
    data = await fetch_video_metadata(url)
    if not data:
        logger.error("[video] No metadata available, cannot extract download URL")
        return None

    download_url = jmespath.search("video.playAddr", data)
    logger.debug(f"[video] Final download URL: {download_url}")
    return download_url
