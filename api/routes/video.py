from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from engine.video import fetch_video_metadata, fetch_video_download_url
import httpx
import random
from typing import Tuple
import os
import json
from bs4 import BeautifulSoup
import logging
import traceback
from urllib.parse import quote
import aiohttp

# --- Load Webshare proxies ---
proxy_file_path = os.path.join(os.path.dirname(__file__), "../../proxies.txt")
try:
    with open(proxy_file_path, "r") as f:
        raw_proxies = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    raw_proxies = []
    print("Warning: proxies.txt not found. Proxying will fail unless fixed.")

def get_random_proxy() -> Tuple[str, dict]:
    proxy_line = random.choice(raw_proxies)
    ip, port, user, pwd = proxy_line.split(":")
    proxy_url = f"http://{user}:{pwd}@{ip}:{port}"
    return proxy_url, {"http://": proxy_url, "https://": proxy_url}

def validate_rapidapi_key(request: Request) -> str:
    key = request.headers.get("x-rapidapi-key")
    if not key:
        raise HTTPException(status_code=401, detail="Missing x-rapidapi-key header")
    return key

async def get_ttdownloader_video_url(tiktok_url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://ttdownloader.com/"
    }

    proxy_line = random.choice(raw_proxies)
    ip, port, user, pwd = proxy_line.split(":")
    proxy_url = f"http://{user}:{pwd}@{ip}:{port}"
    proxies = {"http://": proxy_url, "https://": proxy_url}

    try:
        async with httpx.AsyncClient(headers=headers, proxies=proxies, follow_redirects=True, timeout=30) as client:
            r1 = await client.get("https://ttdownloader.com/")
            soup1 = BeautifulSoup(r1.text, "html.parser")
            token_input = soup1.find("input", {"id": "token"})
            if not token_input or not token_input.get("value"):
                raise ValueError("Token not found")

            token = token_input["value"]
            payload = {"url": tiktok_url, "format": "", "token": token}

            r2 = await client.post("https://ttdownloader.com/req/", data=payload)
            soup2 = BeautifulSoup(r2.text, "html.parser")

            with open("ttdebug.html", "w", encoding="utf-8") as f:
                f.write(soup2.prettify())

            candidates = soup2.find_all("a", href=True, class_="download-link")
            for a in candidates:
                if "Without watermark" in a.text or "No watermark" in a.text:
                    return a["href"]
            for a in candidates:
                if a["href"].startswith("http"):
                    return a["href"]

            raise ValueError("No valid TikTok download link found.")
    except Exception as e:
        print("----- ERROR in TTDownloader -----")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"TTDownloader error: {e}")

router = APIRouter()

@router.get("/video/proxy")
async def proxy_tiktok_video(url: str, request: Request):
    _ = validate_rapidapi_key(request)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/"
    }
    proxy_url, proxies = get_random_proxy()
    try:
        async with httpx.AsyncClient(headers=headers, proxies=proxies, timeout=30) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Proxy fetch failed: {e}")

    return StreamingResponse(
        response.aiter_bytes(),
        media_type="video/mp4",
        headers={
            "Content-Disposition": "inline; filename=video.mp4",
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-cache",
        }
    )

@router.get("/proxy/view", response_class=HTMLResponse)
async def proxy_video_view(url: str, request: Request):
    _ = validate_rapidapi_key(request)
    base_url = str(request.base_url).rstrip("/")
    proxy_endpoint = f"{base_url}/video/proxy?url={quote(url)}"
    return f"""
    <!DOCTYPE html>
    <html><head><title>TikTok Video Viewer</title>
    <style>
        body {{ background: #000; margin: 0; display: flex; align-items: center; justify-content: center; height: 100vh; }}
        video {{ border-radius: 12px; box-shadow: 0 0 20px rgba(255,255,255,0.2); }}
    </style></head><body>
    <video controls autoplay width="320" height="540">
        <source src="{proxy_endpoint}" type="video/mp4">Your browser does not support the video tag.
    </video></body></html>"""

@router.get("/")
async def get_video_metadata(request: Request, url: str = Query(...)):
    _ = validate_rapidapi_key(request)
    try:
        data = await fetch_video_metadata(url)
        if not data:
            raise HTTPException(status_code=404, detail="Video not found or invalid")
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download")
async def get_download_link(request: Request, url: str = Query(...)):
    _ = validate_rapidapi_key(request)
    try:
        download_url = await fetch_video_download_url(url)
        if not download_url:
            raise HTTPException(status_code=404, detail="Download link not found")
        return {"success": True, "url": download_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/ttdownloader")
async def get_download_link_ttdownloader(request: Request, url: str = Query(...)):
    _ = validate_rapidapi_key(request)
    try:
        download_url = await get_ttdownloader_video_url(url)
        return {"success": True, "url": download_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTDownloader error: {e}")

@router.get("/interactions")
async def get_video_interactions(request: Request, url: str = Query(...)):
    _ = validate_rapidapi_key(request)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://www.tikwm.com/api/", params={"url": url})
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="TikWM video API request failed")
        result = response.json()
        if not result.get("data"):
            raise HTTPException(status_code=404, detail="Video data not found")
        data = result["data"]
        return {
            "success": True,
            "video_url": url,
            "title": data.get("title"),
            "like_count": data.get("like_count"),
            "comment_count": data.get("comment_count"),
            "share_count": data.get("share_count"),
            "play_count": data.get("play_count"),
            "cover": data.get("cover"),
            "author": data.get("author")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TikWM interactions fetch error: {e}")

@router.get("/comments")
async def get_video_comments(request: Request, url: str = Query(...)):
    _ = validate_rapidapi_key(request)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch TikTok video page")
        text = response.text
        start_marker = '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
        end_marker = "</script>"
        start = text.find(start_marker)
        end = text.find(end_marker, start)
        if start == -1 or end == -1:
            raise HTTPException(status_code=500, detail="Failed to find comment JSON block")
        json_text = text[start + len(start_marker):end]
        data = json.loads(json_text)
        comments = data.get("__DEFAULT_SCOPE__", {}).get("webapp.video-detail", {}).get("commentList", [])
        return {
            "success": True,
            "comment_count": len(comments),
            "comments": [c.get("comment", {}).get("text", "") for c in comments]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comment extraction failed: {str(e)}")

@router.get("/comments/live")
async def get_live_comments(request: Request, url: str = Query(...)):
    _ = validate_rapidapi_key(request)
    try:
        return fetch_comments_headless(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Headless comment scrape failed: {e}")

@router.post("/batch")
async def batch_video_scrape(request: Request, urls: list[str]):
    _ = validate_rapidapi_key(request)
    try:
        results = []
        for url in urls[:20]:
            data = await fetch_video_metadata(url)
            if data:
                results.append(data)
        return {"success": True, "count": len(results), "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/tkwm")
async def get_tkwm_download_link(request: Request, url: str = Query(...)):
    import aiohttp

    _ = validate_rapidapi_key(request)
    proxy = "http://proxy-rotator-hrst.onrender.com:10000"  # Use your Render proxy rotator

    # Try with proxy first
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.tikwm.com/api/",
                params={"url": url},
                proxy=proxy,
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "Mozilla/5.0"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Proxy request failed with status {response.status}")
                result = await response.json()
                if not result.get("data") or not result["data"].get("play"):
                    raise Exception("Download link not found in proxy mode")
                download_url = result["data"]["play"]
                return {
                    "success": True,
                    "download_url": download_url,
                    "proxy_used": True
                }
    except Exception as proxy_error:
        # Log the proxy error for debugging
        print(f"Proxy mode failed: {proxy_error}")

        # Fallback to direct request (no proxy)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://www.tikwm.com/api/",
                    params={"url": url},
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={"User-Agent": "Mozilla/5.0"}
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Direct request failed with status {response.status}")
                    result = await response.json()
                    if not result.get("data") or not result["data"].get("play"):
                        raise Exception("Download link not found in direct mode")
                    download_url = result["data"]["play"]
                    return {
                        "success": True,
                        "download_url": download_url,
                        "proxy_used": False
                    }
        except Exception as direct_error:
            raise HTTPException(status_code=500, detail=f"TikWM fetch error: Proxy error: {proxy_error} | Direct error: {direct_error}")
