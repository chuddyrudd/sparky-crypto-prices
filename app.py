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

app = FastAPI(title="Crypto Prices API - Free v1")
cache = TTLCache(maxsize=1000, ttl=45)

# Telegram notification setup
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FIRST_HIT_FILE = "/home/jut/crypto-price-mcp/.first_hit_sent"

def send_telegram(message):
    """Send Telegram notification"""
    if not BOT_TOKEN or not CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=data, timeout=5)
        return True
    except:
        return False

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

PORT = int(os.getenv("PORT", 8000))

@app.get("/prices")
@limiter.limit("15/minute")
async def get_prices(request: Request, coins: str = "bitcoin,ethereum,solana,cardano"):
    # Log real IP from Cloudflare headers
    real_ip = request.headers.get('CF-Connecting-IP') or request.headers.get('X-Forwarded-For') or request.client.host
    print(f"[HIT] IP: {real_ip} | Coins: {coins} | Time: {datetime.utcnow().isoformat()}")
    
    # Check for first real external hit (not localhost or local network)
    if not os.path.exists(FIRST_HIT_FILE) and real_ip and not real_ip.startswith(("127.", "192.168.", "10.", "::1")):
        try:
            message = f"🎉 *FIRST REAL HIT!*\n\nIP: `{real_ip}`\nCoins: {coins}\nTime: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\nYour crypto server is live and serving real users!"
            if send_telegram(message):
                # Create flag file so we only notify once
                with open(FIRST_HIT_FILE, 'w') as f:
                    f.write(f"First hit from {real_ip} at {datetime.utcnow().isoformat()}")
                print(f"[NOTIFICATION] First hit alert sent to Telegram!")
        except Exception as e:
            print(f"[ERROR] Failed to send Telegram notification: {e}")
    
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
        "url": "https://fresh-management-studying-slight.trycloudflare.com/prices",
        "capabilities": ["prices", "crypto-data", "real-time-quotes"],
        "protocol": "http"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
