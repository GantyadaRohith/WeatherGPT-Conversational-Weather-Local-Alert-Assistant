# WeatherGPT — Conversational Weather & Local Alert Assistant
**National Level Agentic AI Hackathon (Capabl / ETG)**  
**Track A · A2 | Conversational & RAG-Powered Assistants**

---

## 🌟 Executive Summary
**WeatherGPT** is an agentic AI chatbot platform that delivers real-time meteorological intelligence, 14-day forecasts, Indian farmer crop advisories, extreme disaster alerts, and historical climate trend comparisons. 

It satisfies all **8 core problem requirements** and features the **Compulsory Add-on (Key Feature 7): The Judges' Tool-Selection Trace Panel**, showing live tool dispatch, parameters, latency, and reasoning transparently.

---

## 🚀 Key Features

| # | Requirement | Implementation in WeatherGPT |
|---|---|---|
| 1 | **Real-time weather retrieval** | Live temperature, "feels like", humidity, wind, UV, precipitation via Open-Meteo API. |
| 2 | **Natural language forecasts** | Understands queries like *"Will it rain tomorrow in Varanasi?"* or *"5-day forecast for Pune"*. |
| 3 | **Tool-selection logic** | Dynamic agentic dispatcher choosing between `get_current_weather`, `get_forecast`, `get_crop_advisory`, `get_severe_alerts`, and `get_historical_climate`. |
| 4 | **Extreme weather alerts** | Proactive hazard detection (Cyclonic winds, Cloudbursts >50mm, Heatwaves >40°C, Frost) with visual warnings. |
| 5 | **Location-based advisories** | **Farmer Crop Advisories** (Wheat, Paddy, Cotton, Mustard) for pesticide spraying & irrigation feasibility; **Commuter Advisories** for road & rain safety. |
| 6 | **Multilingual support** | Full native support for **English**, **हिन्दी (Hindi)**, **বাংলা (Bengali)**, **தமிழ் (Tamil)**, **తెలుగు (Telugu)**, and **मराठी (Marathi)**. |
| 7 | **Climate trend analysis** | Compares current observations against historical meteorological archive data from the same week in past years. |
| 8 | **Voice-enabled accessibility** | **Microphone Speech-to-Text (STT)** and **Natural Speech Synthesis (TTS)** for non-literate and rural users. |
| 9 | **Database Persistence (MongoDB)** | **MongoDB Atlas / Local instance** support via `motor` + zero-crash **Persistent JSON Document Store** fallback (`weathergpt_db.json`) for saved locations, alert dispatches, and subscribers. |
| 10 | **Twilio & WhatsApp Cloud API** | Push alerts via **Meta WhatsApp Cloud API** & **Twilio SMS/WhatsApp**, plus a **Live Evaluator Simulator** with realistic delivery receipts (`✓ Delivered`). |
| 11 | **Scheduled Alert Watchdog** | Automated 60-second background watchdog evaluating saved locations against meteorological thresholds and dispatching warnings. |
| **★** | **COMPULSORY ADD-ON** | **Tool-Selection Trace**: Every response renders a trace badge showing tool picked, parameters used, confidence score, and one-line reasoning for hackathon judges! |

---

## 🛠️ Technology Stack
- **Environment**: Isolated Python Virtual Environment (`.venv`) to keep the host clean.
- **Backend**: Python 3.14 + FastAPI + Uvicorn + HTTPX + Pydantic.
- **Meteorological Data**: Live Open-Meteo APIs (Global & Hyperlocal India, 0 API key friction, no rate limit failures).
- **Frontend**: Vanilla HTML5, CSS3 Glassmorphic Design System, Chart.js for 24-hr temperature curves, Web Speech API.

---

## ⚡ How to Run

### Option 1: Double-Click Launcher
Double-click `run.bat` inside the `weathergpt/` directory.

### Option 2: Command Line (PowerShell)
```powershell
cd "c:\capbl hackathon\weathergpt"
.\.venv\Scripts\activate
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
👉 **`http://localhost:8000`**

---

## 🧪 Evaluator & Judge Demo Cheatsheet

Use the built-in quick test buttons on the right sidebar or type these queries:

1. **Current Weather Retrieval (`get_current_weather`)**:
   > *"Current weather and humidity in Mumbai"*
2. **Multi-Day Forecasting (`get_forecast`)**:
   > *"Will it rain tomorrow in Varanasi? Give 5-day forecast"*
3. **Farmer Crop Advisory (`get_crop_advisory`)**:
   > *"Can I spray pesticide on cotton crops in Nagpur this week?"*
4. **Historical Climate Comparison (`get_historical_climate`)**:
   > *"Compare Delhi temperature today vs last year historical climate"*
5. **Extreme Disaster Alert Simulation (`get_severe_alerts`)**:
   > *"Simulate extreme cyclone alert test for Chennai"*
6. **Multilingual Test (Hindi)**:
   > *"वाराणसी में आज का मौसम कैसा है?"*
