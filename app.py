import os
import time
import json
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends
import requests
from cachetools import TTLCache
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from bs4 import BeautifulSoup
from ddgs import DDGS

load_dotenv()

app = FastAPI(title="Sparky Tools - Crypto + Fetch + Search")
cache = TTLCache(maxsize=2000, ttl=300)  # 5 min cache

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

PORT = int(os.getenv("PORT", 8000))

# CRYPTO (unchanged)
@app.get("/prices")
@limiter.limit("15/minute")
async def get_prices(request: Request, coins: str = "bitcoin,ethereum,solana,cardano"):
    key = f"prices_{coins}"
    if key in cache:
        return cache[key]
    try:
        ids = coins.replace(" ", "").lower()
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true", timeout=5)
        r.raise_for_status()
        result = {"timestamp": datetime.utcnow().isoformat(), "prices": r.json(), "source": "CoinGecko via Sparky", "note": "Free v1"}
        cache[key] = result
        return result
    except Exception as e:
        raise HTTPException(500, str(e))

# WEB FETCH (unchanged)
@app.get("/fetch")
@limiter.limit("10/minute")
async def web_fetch(request: Request, url: str):
    if not url.startswith("http"):
        url = "https://" + url
    key = f"fetch_{url}"
    if key in cache:
        return cache[key]
    try:
        r = requests.get(url, headers={"User-Agent": "SparkyBot/1.0"}, timeout=10)
        r.raise_for_status()
        html = r.text
        soup = BeautifulSoup(html, "lxml")
        downloaded = trafilatura.extract(html, include_comments=False, include_tables=True, include_images=True) if 'trafilatura' in globals() else None
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "url": url,
            "title": soup.title.string.strip() if soup.title else None,
            "clean_content": downloaded or soup.get_text(separator=" ", strip=True)[:8000],
            "tables": [t.get_text(strip=True, separator=" | ") for t in soup.find_all("table")],
            "links": [a["href"] for a in soup.find_all("a", href=True)][:30],
            "source": "Sparky Fetch"
        }
        cache[key] = result
        return result
    except Exception as e:
        raise HTTPException(500, str(e))

# === STRUCTURED SEARCH - MAX VOLUME TOOL ===
@app.get("/search")
@limiter.limit("8/minute")
async def web_search(request: Request, q: str):
    key = f"search_{q.lower()}"
    if key in cache:
        return cache[key]
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(q, max_results=10))
            result = {"timestamp": datetime.utcnow().isoformat(), "query": q, "results": results, "source": "DuckDuckGo via Sparky", "note": "Clean structured search - free v1"}
            cache[key] = result
            return result
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "version": "v1-crypto+fetch+search", "uptime": time.time()}

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": "Sparky Tools",
        "description": "Free, fast, no-key tools for AI agents: real-time crypto prices, clean web fetch, structured search.",
        "version": "1.0",
        "url": "https://YOUR-CURRENT-TUNNEL-HERE",
        "protocol": "http",
        "tools": [
            {
                "name": "get_prices",
                "description": "Real-time USD prices + 24h change for any crypto. Cached. Example: ?coins=bitcoin,ethereum",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "coins": {"type": "string", "description": "Comma-separated coin IDs (bitcoin,ethereum,solana,etc)"}
                    }
                }
            },
            {
                "name": "web_fetch",
                "description": "Fetch any URL and return clean structured data: title, content, tables, links, images. No ads/HTML garbage.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Full URL (https:// or example.com)"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "web_search",
                "description": "Structured web search. Returns clean title, url, snippet for top 10 results.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "q": {"type": "string", "description": "Search query"}
                    },
                    "required": ["q"]
                }
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
