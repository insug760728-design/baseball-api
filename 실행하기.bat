@echo off
chcp 65001 > nul
title 스포츠 데이터 관리 시스템
cd /d "%~dp0"

echo ========================================================
echo  스포츠 데이터 수집 & 앱 관리 서버 실행 중...
echo  잠시 후 브라우저(http://localhost:8000/)가 자동으로 열립니다.
echo ========================================================

python run.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [오류] Python 실행에 실패했습니다. Python이 정상적으로 설치되어 있는지 확인해주세요.
    pause
)
pause