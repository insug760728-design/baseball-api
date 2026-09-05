@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 방금 끝난 야구 경기 원클릭 자동 수집기
python sync_latest.py
pause
