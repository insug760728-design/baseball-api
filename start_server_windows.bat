@echo off
chcp 65001 > nul
title TOKEON Sports API Server
echo ==============================================================================
echo 🚀 TOKEON Sports API Server (Windows Optimized Mode)
echo ==============================================================================
echo.
echo Checking Python environment...
python -c "import uvicorn, sqlalchemy; print('Dependencies OK')"
if errorlevel 1 (
    echo [ERROR] Python environment or dependencies missing. Please install requirements.
    pause
    exit /b 1
)

echo.
echo Starting server with WindowsSelectorEventLoopPolicy and SQLite WAL mode...
python run_server.py
pause
