# Sparky Tools API — Crypto + Web Fetch

[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Agent%20Ready-purple)](https://openclaw.ai)

> **Free HTTP API for AI Agents** — Real-time cryptocurrency prices + intelligent web scraping. No API keys, no rate limits for personal use, built for OpenClaw and other AI agent platforms.

**Keywords:** `ai agent api`, `crypto price api`, `web scraping api`, `openclaw tools`, `agent web fetch`, `mcp alternative`, `free crypto api`, `structured web extraction`, `ai agent http tools`, `fastapi agent server`

---

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [GET /prices](#get-prices)
  - [GET /fetch](#get-fetch)
  - [GET /health](#get-health)
  - [GET /.well-known/agent.json](#get-well-knownagentjson)
- [OpenClaw Agent Integration](#openclaw-agent-integration)
- [Use Cases](#use-cases)
- [Deployment](#deployment)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [License](#license)

---

## ✨ Features

| Feature | Endpoint | Cache | Rate Limit |
|---------|----------|-------|------------|
| **Crypto Prices** | `/prices` | 45 sec | 15/min |
| **Web Scraping** | `/fetch` | 10 min | 10/min |
| **Health Check** | `/health` | none | none |
| **Agent Discovery** | `/.well-known/agent.json` | none | none |

### Crypto Prices (`/prices`)
- ✅ 1000+ cryptocurrencies via CoinGecko
- ✅ Real-time USD prices + 24h change
- ✅ No CoinGecko API key required
- ✅ Smart caching reduces API calls

### Web Fetch (`/fetch`)
- ✅ **Intelligent content extraction** — no HTML garbage
- ✅ Extracts: title, meta, article text, tables, links, images
- ✅ Uses `trafilatura` + `BeautifulSoup` (battle-tested stack)
- ✅ Perfect for AI agents that need clean web content
- ✅ Caches results per URL (10 minutes)

### For AI Agents
- ✅ **OpenClaw compatible** — HTTP REST, no MCP complexity
- ✅ Structured JSON responses
- ✅ `.well-known/agent.json` for auto-discovery
- ✅ Copy-paste ready integration examples

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/chuddyrudd/sparky-crypto-prices.git
cd sparky-crypto-prices

# 2. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run
python3 app.py
# Server starts on http://localhost:8000

# 4. Test
curl http://localhost:8000/health
```

---

## 📚 API Reference

### GET /prices

Real-time cryptocurrency prices.

```bash
curl "http://localhost:8000/prices?coins=bitcoin,ethereum,solana"
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `coins` | string | `bitcoin,ethereum,solana,cardano` | Comma-separated CoinGecko IDs |

**Response:**
```json
{
  "timestamp": "2026-02-26T11:45:00",
  "prices": {
    "bitcoin": { "usd": 67245.00, "usd_24h_change": 2.5 },
    "ethereum": { "usd": 3521.40, "usd_24h_change": -1.2 },
    "solana": { "usd": 145.20, "usd_24h_change": 5.1 }
  },
  "source": "CoinGecko cached via Sparky",
  "note": "Upgrade to paid v2 coming"
}
```

**Supported Coins:** Any CoinGecko ID. Common: `bitcoin`, `ethereum`, `solana`, `cardano`, `polkadot`, `dogecoin`, `chainlink`, `avalanche`

---

### GET /fetch

Intelligent web content extraction.

```bash
curl "http://localhost:8000/fetch?url=example.com"
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `url` | string | Yes | Any URL (https:// auto-added if missing) |

**Response:**
```json
{
  "timestamp": "2026-02-26T11:45:00",
  "url": "https://example.com",
  "title": "Example Domain",
  "meta_description": "This domain is for use in illustrative examples...",
  "clean_content": "Clean article text without ads or HTML tags...",
  "tables": [],
  "links": ["https://example.com/page1", "https://example.com/page2"],
  "images": ["https://example.com/image.jpg"],
  "source": "Sparky Web Fetch (requests + trafilatura)",
  "note": "Clean, no ads, no HTML garbage. Use ?url=example.com"
}
```

**Use Cases:**
- Research: Extract article content for AI analysis
- Data mining: Scrape structured data from websites
- Monitoring: Track changes on web pages
- Integration: Feed clean content to LLMs

---

### GET /health

Health check endpoint.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "version": "v1-crypto+webfetch",
  "uptime": 1772120121.51
}
```

---

### GET /.well-known/agent.json

Agent discovery card for AI platforms.

```bash
curl http://localhost:8000/.well-known/agent.json
```

**Response:**
```json
{
  "name": "Sparky Tools Oracle",
  "description": "Crypto prices + Web Fetch (clean structured URL to JSON). Free v1.",
  "url": "https://your-tunnel-url/prices or /fetch?url=",
  "capabilities": ["crypto-prices", "web-fetch", "structured-scrape"],
  "protocol": "http"
}
```

---

## 🤖 OpenClaw Agent Integration

This API is built for **OpenClaw** and other AI agent platforms.

### Basic Usage

```python
# Get crypto prices
result = web_fetch("http://localhost:8000/prices?coins=bitcoin,ethereum")
# Returns: {"prices": {"bitcoin": {"usd": 67245, ...}}}

# Scrape web content
result = web_fetch("http://localhost:8000/fetch?url=news.ycombinator.com")
# Returns: {"title": "Hacker News", "clean_content": "...", "links": [...]}
```

### Advanced Agent Workflows

```python
# 1. Research workflow
def research_topic(topic):
    # Search for topic
    search_url = f"https://en.wikipedia.org/wiki/{topic}"
    content = web_fetch(f"http://localhost:8000/fetch?url={search_url}")
    return content["clean_content"]

# 2. Crypto tracking workflow
def track_crypto_portfolio(coins):
    prices = web_fetch(f"http://localhost:8000/prices?coins={coins}")
    return prices["prices"]

# 3. Combined workflow
def analyze_crypto_news(coin):
    # Get price
    price_data = web_fetch(f"http://localhost:8000/prices?coins={coin}")
    # Get news context
    news = web_fetch(f"http://localhost:8000/fetch?url=coinmarketcap.com/currencies/{coin}/news")
    return {"price": price_data, "context": news["clean_content"]}
```

### Why HTTP REST > MCP for Agents

| | HTTP REST (This API) | MCP |
|---|----------------------|-----|
| **Setup** | One URL, instant | Complex config, stdio |
| **Compatibility** | Works everywhere | Only MCP-aware clients |
| **Debugging** | curl, browser | Harder to troubleshoot |
| **Agent Access** | `web_fetch()` tool | Special client required |
| **Discovery** | `.well-known/agent.json` | Manual configuration |

---

## 💡 Use Cases

### For Crypto Traders
```bash
# Track Bitcoin price
curl "localhost:8000/prices?coins=bitcoin"

# Track portfolio
curl "localhost:8000/prices?coins=bitcoin,ethereum,solana,cardano,polkadot"
```

### For Researchers
```bash
# Extract article content
curl "localhost:8000/fetch?url=medium.com/article-about-ai"

# Scrape documentation
curl "localhost:8000/fetch?url=docs.python.org/3/tutorial"
```

### For AI Agents
```python
# Your OpenClaw agent can now:
# 1. Check crypto prices
# 2. Scrape web content
# 3. Build knowledge bases
# 4. Monitor websites for changes
```

---

## 🌐 Deployment

### Local Development
```bash
python3 app.py
```

### Public URL (Cloudflare Tunnel)
```bash
cloudflared tunnel --url http://localhost:8000
```

### Production (PM2)
```bash
npm install -g pm2
pm2 start app.py --name sparky-api --interpreter python3
pm2 save
pm2 startup
```

### Production (systemd)
```bash
# Copy service file (create your own)
sudo cp sparky-api.service /etc/systemd/system/
sudo systemctl enable sparky-api
sudo systemctl start sparky-api
```

---

## 🏗️ Architecture

```
┌─────────────┐     HTTP GET     ┌─────────────────┐     HTTPS     ┌──────────────┐
│   Client    │◄────────────────►│  FastAPI Server │◄────────────►│  CoinGecko   │
│  (Any HTTP) │    JSON Response │  (this repo)    │   REST API    │     API      │
└─────────────┘                  └─────────────────┘               └──────────────┘
                                        │
                                        ▼
                              ┌───────────────────┐
                              │   Web Pages       │
                              │   (any URL)       │
                              └───────────────────┘
```

**Stack:**
- **Framework:** FastAPI (high-performance Python)
- **Web Extraction:** trafilatura + BeautifulSoup + lxml
- **Rate Limiting:** slowapi
- **Caching:** cachetools (TTLCache)
- **Server:** uvicorn (ASGI)

---

## ⚙️ Configuration

Create `.env` file:

```env
PORT=8000
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_BOT_CHAT_ID=your_chat_id_here
```

**Optional:** Telegram notifications on first external hit.

---

## 📄 License

MIT © 2026 chuddyrudd

---

**Built for AI Agents. Powered by OpenClaw. Free forever.**

**Search:** `ai agent api`, `crypto api free`, `web scraping api`, `openclaw agent tools`, `fastapi agent server`, `mcp alternative http`
