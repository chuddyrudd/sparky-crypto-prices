# HerdOfWorms Crypto Prices API

Real-time cryptocurrency prices via HTTP API. Free, cached, rate-limited access to CoinGecko data.

**⚠️ Note:** This is an HTTP REST API server, not an MCP (Model Context Protocol) server.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/chuddyrudd/sparky-crypto-prices.git
cd sparky-crypto-prices
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python3 app.py
```

Server starts on `http://localhost:8000`

## API Endpoints

### GET /prices
Get current USD prices for specified cryptocurrencies.

```bash
curl "http://localhost:8000/prices?coins=bitcoin,ethereum,solana"
```

**Parameters:**
- `coins` (optional): Comma-separated list of CoinGecko IDs. Default: `bitcoin,ethereum,solana,cardano`

**Response:**
```json
{
  "timestamp": "2026-02-26T11:45:00",
  "prices": {
    "bitcoin": { "usd": 67245.00, "usd_24h_change": 2.5 },
    "ethereum": { "usd": 3521.40, "usd_24h_change": -1.2 }
  },
  "source": "CoinGecko cached via Sparky (free v1)"
}
```

### GET /health
Health check endpoint.

```bash
curl http://localhost:8000/health
```

### GET /.well-known/agent.json
Agent card for discovery.

## Features

- ✅ 1000+ cryptocurrencies (any CoinGecko-supported coin)
- ✅ 45-second cache (reduces API calls)
- ✅ Rate limited: 15 requests/minute per IP
- ✅ 24-hour price change data
- ✅ Telegram notification on first real external hit
- ✅ No API key required

## Supported Coins

Any CoinGecko ID works. Common examples:
- `bitcoin`, `ethereum`, `solana`, `cardano`, `polkadot`
- `dogecoin`, `shiba-inu`, `chainlink`, `avalanche`

Full list: [CoinGecko Coins List](https://api.coingecko.com/api/v3/coins/list)

## Configuration

Create a `.env` file:

```env
PORT=8000
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

**Note:** Telegram notifications are optional. If not configured, the server works normally without them.

## Deployment

### Local
```bash
python3 app.py
```

### With Cloudflare Tunnel (Public URL)
```bash
cloudflared tunnel --url http://localhost:8000
```

### Production
Use a process manager like `systemd` or `pm2`:

```bash
# Using pm2
pm2 start app.py --name crypto-api --interpreter python3
```

## Architecture

```
┌─────────────┐     HTTP GET     ┌─────────────────┐     HTTPS     ┌──────────────┐
│   Client    │◄────────────────►│  FastAPI Server │◄────────────►│  CoinGecko   │
│  (Any HTTP) │    JSON Response │  (this repo)    │   REST API    │     API      │
└─────────────┘                  └─────────────────┘               └──────────────┘
```

- **Framework:** FastAPI
- **Cache:** TTLCache (45 seconds)
- **Rate Limiting:** slowapi (15/min per IP)
- **Data Source:** CoinGecko API (free tier)

## Requirements

- Python 3.8+
- `fastapi`, `uvicorn`, `requests`, `cachetools`, `slowapi`, `python-dotenv`

See `requirements.txt` for full list.

## Troubleshooting

**"Module not found" errors**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Port already in use**
```bash
# Change port in .env or:
PORT=8080 python3 app.py
```

## License

MIT © 2026 chuddyrudd
