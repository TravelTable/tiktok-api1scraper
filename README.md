# TikTok Scraper API (FastAPI)

Production-ready API to scrape TikTok videos, comments, profiles, hashtags, and more — no login or paid services required.

---

## 🚀 Endpoints

| Endpoint             | Description                                |
|----------------------|--------------------------------------------|
| `GET /video`         | Scrape metadata for a TikTok video         |
| `GET /video/download`| Get direct video download URL              |
| `POST /video/batch`  | Batch scrape up to 20 video URLs           |
| `GET /comments`      | Get paginated comments from a video        |
| `GET /profile`       | Get TikTok user profile info               |
| `GET /user/posts`    | Fetch user’s latest videos                 |
| `GET /user/stats`    | Get user stats (followers, avg views, etc) |
| `GET /user/metadata/raw` | Raw TikTok JSON metadata             |
| `GET /channel`       | Get all videos from a user's feed          |
| `GET /search`        | Search videos and users by keyword         |
| `GET /hashtag`       | Get data about a hashtag                   |
| `GET /trending`      | Get trending videos by region              |

---

## 🌐 Run Locally

```bash
git clone https://github.com/your-user/tiktok-scraper-api
cd tiktok-scraper-api
pip install -r requirements.txt
uvicorn main:app --reload
