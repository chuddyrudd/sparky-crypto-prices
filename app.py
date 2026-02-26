import os
import json
import time
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
import requests
from cachetools import TTLCache
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

app = FastAPI(title="HerdOfWorms Crypto Prices - Free v1")
cache = TTLCache(maxsize=1000, ttl=45)

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

PORT = int(os.getenv("PORT", 8000))

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
            "source": "CoinGecko cached via Sparky (free v1)",
            "note": "Upgrade to paid v2 coming soon - ?coins=bitcoin,ethereum"
        }
        cache[key] = result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "uptime": time.time(), "version": "free-v1"}

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": "Sparky Crypto Prices Oracle",
        "description": "Real-time cached CoinGecko USD prices + 24h change. Free v1, no key, rate limited. Paid x402 v2 soon.",
        "url": "https://606fed64773215ab-143-105-23-12.serveousercontent.com/prices",
        "capabilities": ["prices", "crypto-data", "real-time-quotes"],
        "protocol": "http"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
