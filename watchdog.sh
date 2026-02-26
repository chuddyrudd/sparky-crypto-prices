#!/bin/bash
# Crypto Server Watchdog - Runs every 60 seconds via cron
# Auto-restarts server if down, logs alerts for Sparky

LOG_FILE="/home/jut/crypto-price-mcp/ALERTS.log"
SERVER_SCREEN="crypto-server"
TUNNEL_SCREEN="tunnel"
LOCAL_URL="http://localhost:8000/health"
PUBLIC_URL="https://fresh-management-studying-slight.trycloudflare.com/health"

check_and_restart() {
    local name=$1
    local screen_name=$2
    local restart_cmd=$3
    
    # Check if screen session exists
    if ! screen -ls | grep -q "$screen_name"; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: $name screen session missing. Restarting..." >> "$LOG_FILE"
        eval "$restart_cmd"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $name restarted" >> "$LOG_FILE"
        return 1
    fi
    return 0
}

# Check server screen
check_and_restart "crypto-server" "$SERVER_SCREEN" "cd /home/jut/crypto-price-mcp && screen -S $SERVER_SCREEN -dm bash -c 'source venv/bin/activate && python app.py'"
SERVER_OK=$?

# Check tunnel screen  
check_and_restart "tunnel" "$TUNNEL_SCREEN" "screen -S $TUNNEL_SCREEN -dm bash -c 'cloudflared tunnel --url http://localhost:8000 2>&1 | tee /tmp/tunnel.log'"
TUNNEL_OK=$?

# Check local endpoint responds
if ! curl -s -m 3 "$LOCAL_URL" > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: Local server not responding on port 8000" >> "$LOG_FILE"
    # Kill and restart
    pkill -f "python app.py" 2>/dev/null
    cd /home/jut/crypto-price-mcp && screen -S $SERVER_SCREEN -dm bash -c 'source venv/bin/activate && python app.py'
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: Server hard-restarted due to unresponsive" >> "$LOG_FILE"
fi

# Check public endpoint
if ! curl -s -m 5 "$PUBLIC_URL" > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARN: Public tunnel not responding (may be temporary)" >> "$LOG_FILE"
fi

# Cleanup old alerts (keep last 100 lines)
tail -100 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"

exit 0
