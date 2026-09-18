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

# Run with Gunicorn + Uvicorn Workers (Render 512MB RAM Safe: 1 Worker Mode)
PORT_TO_BIND="${PORT:-8000}"
exec gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app \
    --bind 0.0.0.0:${PORT_TO_BIND} \
    --max-requests 500 \
    --max-requests-jitter 50 \
    --timeout 120 \
    --graceful-timeout 30 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --pid logs/tokeon.pid
