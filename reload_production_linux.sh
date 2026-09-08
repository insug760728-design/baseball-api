#!/bin/bash
# ==============================================================================
# TOKEON Sports Analytics - Zero-Downtime Graceful Reload Script
# ==============================================================================

echo "=========================================================="
echo "🔄 Executing Zero-Downtime Reload for TOKEON Sports API..."
echo "=========================================================="

PID_FILE="logs/tokeon.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Sending SIGHUP to Master Gunicorn Process (PID: $PID)..."
        kill -HUP "$PID"
        echo "✅ Reload signal sent! Gunicorn is cycling worker processes gracefully."
        echo "Users experience ZERO downtime or disconnection."
        exit 0
    fi
fi

# Fallback: search by process pattern
echo "PID file not found or inactive. Searching for running gunicorn process..."
MASTER_PID=$(pgrep -f "gunicorn.*app.main:app" | head -n 1)

if [ -n "$MASTER_PID" ]; then
    echo "Found master process at PID $MASTER_PID. Sending SIGHUP..."
    kill -HUP "$MASTER_PID"
    echo "✅ Reload signal sent successfully!"
else
    echo "❌ No active Gunicorn process found. Please start the server first using ./run_production_linux.sh"
    exit 1
fi
