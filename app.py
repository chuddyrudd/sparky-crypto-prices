import os
import time
import json
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
import requests
from cachetools import TTLCache
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from bs4 import BeautifulSoup
import trafilatura

load_dotenv()

app = FastAPI(title="Sparky Tools - Crypto + Web Fetch v1")
cache = TTLCache(maxsize=2000, ttl=600)  # 10 min cache per URL

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

PORT = int(os.getenv("PORT", 8000))

# === CRYPTO PRICES (unchanged) ===
@app.get("/prices")
@limiter.limit("15/minute")
async def get_prices(request: Request, coins: str = "bitcoin,ethereum,solana,cardano"):
    key = f"prices_{coins}"
    if key in cache:
        return cache[key]
    try:
        ids = coins.replace(" ", "").lower()
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "prices": data,
            "source": "CoinGecko cached via Sparky",
            "note": "Upgrade to paid v2 coming"
        }
        cache[key] = result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === WEB FETCH - HIGH DEMAND TOOL ===
@app.get("/fetch")
@limiter.limit("10/minute")
async def web_fetch(request: Request, url: str):
    """Clean structured fetch: title, content, tables, links, images, meta. Cached."""
    if not url.startswith("http"):
        url = "https://" + url
    key = f"fetch_{url}"
    if key in cache:
        return cache[key]
    try:
        headers = {"User-Agent": "SparkyBot/1.0 (https://github.com/chuddyrudd/sparky-crypto-prices)"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        html = resp.text
        # Clean extraction downloaded
        downloaded = trafilatura.extract(html, include_comments=False, include_tables=True, include_images=True)
        soup = BeautifulSoup(html, "lxml")
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "url": url,
            "title": soup.title.string.strip() if soup.title else None,
            "meta_description": soup.find("meta", attrs={"name": "description"})["content"] if soup.find("meta", attrs={"name": "description"}) else None,
            "clean_content": downloaded or "No clean text found",
            "tables": [table.get_text(strip=True, separator=" | ") for table in soup.find_all("table")],
            "links": [a.get("href") for a in soup.find_all("a", href=True)][:50],
            "images": [img.get("src") for img in soup.find_all("img", src=True)][:20],
            "source": "Sparky Web Fetch (requests + trafilatura)",
            "note": "Clean, no ads, no HTML garbage. Use ?url=example.com"
        }
        cache[key] = result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "version": "v1-crypto+webfetch", "uptime": time.time()}

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": "Sparky Tools Oracle",
        "description": "Crypto prices + Web Fetch (clean structured URL to JSON). Free v1, no key, rate limited. x402 v2 soon.",
        "url": "https://fresh-management-studying-slight.trycloudflare.com/prices or /fetch?url=",
        "capabilities": ["crypto-prices", "web-fetch", "structured-scrape"],
        "protocol": "http"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
