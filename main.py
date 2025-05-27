from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.routes import comments_browser
from api.routes import (
    video,
    comments,
    profile,
    user,
    channel,
    search,
    hashtag,
    trending
)

app = FastAPI(
    title="TikTok Scraper API",
    description="Production-ready API to scrape TikTok videos, comments, profiles, hashtags, and more — no login, no paid APIs.",
    version="1.0.0"
)

# CORS middleware (safe to keep wide open for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 Global RapidAPI auth middleware
@app.middleware("http")
async def enforce_rapidapi_key(request: Request, call_next):
    if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
        return await call_next(request)
    if not request.headers.get("x-rapidapi-key"):
        raise HTTPException(status_code=401, detail="Missing x-rapidapi-key header")
    return await call_next(request)

# Register all route modules
app.include_router(video.router, prefix="/video", tags=["Video"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])
app.include_router(profile.router, prefix="/profile", tags=["Profile"])
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(channel.router, prefix="/channel", tags=["Channel"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(hashtag.router, prefix="/hashtag", tags=["Hashtag"])
app.include_router(trending.router, prefix="/trending", tags=["Trending"])
app.include_router(comments_browser.router, prefix="/tiktok", tags=["TikTok Browser Scraper"])
