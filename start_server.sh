#!/bin/bash
# Robust crypto server start script - kills old processes, starts fresh

PIDFILE="/tmp/crypto-server.pid"
PORT=8000

echo "[$(date)] Starting crypto server..."

# Kill any existing process on port 8000
echo "[$(date)] Checking for existing processes on port $PORT..."
lsof -ti:$PORT | xargs kill -9 2>/dev/null
sleep 1

# Kill any lingering python app.py processes
pkill -9 -f "python3 app.py" 2>/dev/null
sleep 1

# Clean up old screen sessions
screen -S crypto-server -X quit 2>/dev/null

# Change to server directory
cd /home/jut/crypto-price-mcp || exit 1
source venv/bin/activate

# Start server in screen for persistence
echo "[$(date)] Starting server in screen session..."
screen -S crypto-server -dm bash -c "python3 app.py"

# Wait for startup
sleep 2

# Verify it's running
if curl -s http://localhost:$PORT/health > /dev/null; then
    echo "[$(date)] ✅ Server started successfully"
    # Save PID
    lsof -ti:$PORT > $PIDFILE
    exit 0
else
    echo "[$(date)] ❌ Server failed to start"
    exit 1
fi
