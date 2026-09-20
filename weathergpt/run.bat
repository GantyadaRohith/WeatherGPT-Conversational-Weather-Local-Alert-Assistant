@echo off
title "WeatherGPT - AI Weather & Alert Assistant"
echo ========================================================
echo Starting WeatherGPT (Problem Statement A2)
echo Python Virtual Environment: .venv
echo Server URL: http://127.0.0.1:8000
echo ========================================================
cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
) else (
    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
)
pause
