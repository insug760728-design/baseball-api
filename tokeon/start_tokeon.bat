@echo off
chcp 65001 > nul
echo ====================================================
echo  🚀 TOKEON V2 실시간 스포츠 분석 포털 서버 시작 (Port 8080)
echo ====================================================
cd /d "%~dp0\.."
python -m uvicorn tokeon.main:app --host 0.0.0.0 --port 8080 --reload
pause
