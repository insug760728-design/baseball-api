#!/bin/bash
# ==============================================================================
# TOKEON Sports Analytics - Linux Production Startup Script (Zero-Downtime Ready)
# ==============================================================================

# Ensure logs directory exists
mkdir -p logs

echo "=========================================================="
echo "🚀 Starting TOKEON Sports API in High-Performance Mode..."
echo "=========================================================="

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Port 8000 is already in use. Please check running processes."
fi

# Run with Gunicorn + Uvicorn Workers
# -w 4: 4 worker processes to handle concurrent requests
# -k uvicorn.workers.UvicornWorker: Async ASGI worker
# --timeout 120: Long-polling & heavy query protection
# --graceful-timeout 30: Ensures in-flight requests finish before reload
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --graceful-timeout 30 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --pid logs/tokeon.pid
