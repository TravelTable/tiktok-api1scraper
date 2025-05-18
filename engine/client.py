import httpx
import os

USE_PROXY = os.getenv("USE_PROXY", "0") == "1"
PROXY_URL = os.getenv("PROXY_URL", "")  # Optional: add to .env for dynamic proxy config

def get_http_client():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    if USE_PROXY and PROXY_URL:
        return httpx.AsyncClient(headers=headers, proxies=PROXY_URL, timeout=15)
    else:
        return httpx.AsyncClient(headers=headers, timeout=15)
