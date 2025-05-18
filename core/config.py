import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "development")
USE_PROXY = os.getenv("USE_PROXY", "0") == "1"

# Optional: add a proxy URL here (or load it from .env later)
PROXY_URL = os.getenv("PROXY_URL", "http://your-proxy.com")  # ← optional if using rotating proxies
