from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.routes import (
    video,
    comments,
    profile,
    user,
    channel,
    search,
    hashtag,
    trending,
    comments_browser,   # <- included here for completeness!
)

app = FastAPI(
    title="TikTok Scraper API",
    description="Production-ready API to scrape TikTok videos, comments, profiles, hashtags, and more — no login, no paid APIs.",
    version="1.0.0"
)

# Open CORS for all origins (safe for RapidAPI/public use, restrict in production if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API route modules
app.include_router(video.router, prefix="/video", tags=["Video"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])
app.include_router(profile.router, prefix="/profile", tags=["Profile"])
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(channel.router, prefix="/channel", tags=["Channel"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(hashtag.router, prefix="/hashtag", tags=["Hashtag"])
app.include_router(trending.router, prefix="/trending", tags=["Trending"])
app.include_router(comments_browser.router, prefix="/comments-browser", tags=["Comments Browser"])  # <- Add this line for comments_browser
