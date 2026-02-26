#!/bin/bash
# Monitor crypto server - restart if down, notify on new hits

LOG_FILE="/home/jut/crypto-price-mcp/server.log"
STATE_FILE="/home/jut/crypto-price-mcp/.last_hit_check"
START_SCRIPT="/home/jut/crypto-price-mcp/start_server.sh"
BOT_TOKEN="8450255612:AAED3PBmTQpkM1kJd2ANpjQpPKkLEB6Vihk"
CHAT_ID="8309678126"

# First check if server is alive
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "[$(date)] Server down - restarting..."
    $START_SCRIPT
    
    # Send restart notification
    MESSAGE="⚠️ *Crypto Server Was Down — Auto-Restarted*\n\nTime: $(date -u '+%Y-%m-%d %H:%M:%S') UTC\nStatus: Restarted via monitor"
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=$MESSAGE" \
        -d "parse_mode=Markdown" > /dev/null 2>&1
fi

# Check for new external hits (non-localhost) since last check
NEW_HITS=$(grep "\[HIT\]" "$LOG_FILE" 2>/dev/null | grep -v "127\.\|192\.168\.\|10\.\|::1" | tail -5)

if [ -n "$NEW_HITS" ]; then
    # Extract the most recent hit
    LATEST_HIT=$(echo "$NEW_HITS" | tail -1)
    HIT_IP=$(echo "$LATEST_HIT" | grep -oP 'IP: \K[^ ]+')
    
    # Send Telegram notification
    MESSAGE="🚀 *New Crypto API Hit!*\n\nIP: \`$HIT_IP\`\nTime: $(date -u '+%Y-%m-%d %H:%M:%S') UTC\n\nServer getting traffic!"
    
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=$MESSAGE" \
        -d "parse_mode=Markdown" > /dev/null 2>&1
fi

# Update last check time
date -u +%s > "$STATE_FILE"
