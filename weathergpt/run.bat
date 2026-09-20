@echo off
title WeatherGPT - AI Weather & Alert Assistant
echo ========================================================
echo Starting WeatherGPT (Problem Statement A2)
echo Python Virtual Environment: .venv
echo Server URL: http://127.0.0.1:8000
echo ========================================================
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
