# 🌦️ WeatherGPT — Conversational Weather & Local Alert Assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.0+-646CFF.svg)](https://vitejs.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-FF6F00.svg)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **National Level Agentic AI Hackathon (Capabl / ETG)**  
> **Track A · Problem Statement A2: Conversational Weather & Local Alert Assistant**

---

## 🌟 Overview & Architecture

**WeatherGPT** is a production-grade, agentic AI weather intelligence platform. It combines live meteorological observation APIs, LangChain/LangGraph tool calling, crop safety heuristics, and extreme disaster alert detection into a sleek, Apple Weather-inspired glassmorphic React interface.

```
                  ┌───────────────────────────────┐
                  │    React 19 + Vite Frontend   │
                  │ (Hero, 24h Chart, Radar, STT) │
                  └──────────────┬────────────────┘
                                 │ HTTP / JSON
                                 ▼
                  ┌───────────────────────────────┐
                  │        FastAPI Gateway        │
                  └──────────────┬────────────────┘
                                 │
                   LangGraph StateGraph / Router
                                 │
      ┌──────────────────────────┼──────────────────────────┐
      ▼                          ▼                          ▼
┌──────────────┐         ┌──────────────┐          ┌────────────────┐
│ Multi-LLM    │         │ Meteorological│         │ Anti-          │
│ Engine       │         │ Tool Registry│          │ Hallucination  │
│ (Groq / LLaMA│         │ (Open-Meteo  │          │ Guard & Metric │
│  Gemini /    │         │  Live APIs)  │          │ Verification   │
│  Local Agent)│         │              │          │                │
└──────────────┘         └──────────────┘          └────────────────┘
                                 │
                                 ▼
              [Judges' Live Tool-Selection Trace Panel]
```

---

## 🚀 Key Features Matrix

| # | Requirement | Implementation in WeatherGPT |
|---|---|---|
| **1** | **Real-Time Weather Retrieval** | Instant temperature, "feels like", relative humidity, wind speed & direction, UV index, and precipitation probability via high-resolution Open-Meteo APIs. |
| **2** | **Natural Language Forecasting** | Understands multi-day queries (e.g., *"Will it rain tomorrow in Varanasi?"* or *"7-day forecast for Visakhapatnam"*). |
| **3** | **Agentic Tool Selection** | Dynamic LangGraph agent autonomously selecting tools (`get_current_weather`, `get_forecast`, `get_crop_advisory`, `get_severe_alerts`, `get_historical_climate`). |
| **4** | **Extreme Disaster Alerts** | Real-time hazard detection with threat levels (Advisory, Watch, Warning) for cyclonic winds, cloudbursts (>50mm), heatwaves (>40°C), and ground frost. |
| **5** | **Agricultural & Commuter Advisories** | **Farmer Crop Advisory**: Spraying feasibility & irrigation planning for Wheat, Paddy, Cotton, and Mustard. **Commuter Advisory**: Road spray and visibility warnings. |
| **6** | **Multilingual Support** | Native Indian language support for **English**, **हिन्दी (Hindi)**, **తెలుగు (Telugu)**, **বাংলা (Bengali)**, **தமிழ் (Tamil)**, and **मराठी (Marathi)**. |
| **7** | **Historical Climate Comparison** | Compares today's observations against meteorological archives from the exact same calendar week across previous years. |
| **8** | **Voice STT & TTS** | Microphone Speech-to-Text and browser speech synthesis for hands-free and rural farmer accessibility. |
| **★** | **COMPULSORY ADD-ON** | **Judges' Tool-Selection Trace Panel**: Displays tool called, extracted parameters, execution latency (ms), confidence rating, and reasoning for full auditability. |

---

## 🗂️ Project Structure

```
capbl-hackathon/
├── Capabl_Agentic_AI_Hackathon_Problem_Statements_Updated.pdf
├── README.md
├── .gitignore
└── weathergpt/
    ├── run.bat                          # One-click Windows launcher
    ├── requirements.txt                 # Backend Python dependencies
    ├── .env.example                     # Environment template (safe for git)
    ├── backend/
    │   ├── main.py                      # FastAPI REST application
    │   ├── langgraph_agent.py           # LangGraph Tool-calling agent workflow
    │   ├── llm_client.py                # Multi-provider LLM router (Groq/Gemini/Local)
    │   ├── weather_tools.py             # Open-Meteo tool bindings & alias resolver
    │   ├── alerts.py                    # Disaster severity heuristics
    │   ├── advisories.py                # Agricultural spraying & crop advisory logic
    │   └── translations.py              # Indic language localization tables
    └── react_frontend/
        ├── package.json
        ├── vite.config.js
        ├── index.html
        └── src/
            ├── App.jsx                  # Main React dashboard
            ├── index.css                # Glassmorphic Apple-style design tokens
            └── components/
                ├── FixedWeatherHero.jsx # Pinned location hero card
                ├── WeatherTelemetryGrid.jsx # Metric cards & hourly curves
                ├── AgroAdvisoryCard.jsx # Farmer crop & spraying feasibility
                ├── TracePanel.jsx       # Judges' tool dispatch inspector
                └── SettingsModal.jsx    # Live LLM provider selector
```

---

## ⚡ Quick Start

### 1. Automated Launcher (Windows)
Double-click [`weathergpt/run.bat`](weathergpt/run.bat) to automatically install requirements and launch the FastAPI server.

### 2. Manual Setup

#### Backend:
```bash
cd weathergpt
python -m venv .venv

# Windows
.\.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend (React / Vite):
```bash
cd weathergpt/react_frontend
npm install
npm run dev
```

Visit **`http://localhost:5173`** (React UI) or **`http://localhost:8000`** (FastAPI backend).

---

## 🔑 LLM Provider Configuration

WeatherGPT runs out of the box with zero required API keys using its built-in **Local Smart Agent**.

To enable cloud LLM reasoning with tool calling:
1. Copy `.env.example` to `.env`:
   ```bash
   cp weathergpt/.env.example weathergpt/.env
   ```
2. Enter your API key:
   - **Groq** (Recommended, blazing fast): `GROQ_API_KEY=gsk_...`
   - **Gemini**: `GEMINI_API_KEY=AIza...`
   - **OpenAI**: `OPENAI_API_KEY=sk-...`

*(Note: `.env` is protected by `.gitignore` and is never committed to Git).*

---

## 🧪 Evaluator & Judge Test Queries

| Scenario | Query | Expected Tool Dispatch |
|---|---|---|
| **Current Weather** | *"What is the weather and humidity in Visakhapatnam right now?"* | `get_current_weather` |
| **Multi-Day Forecast** | *"Give me a 5-day forecast for Varanasi with rain predictions"* | `get_forecast` |
| **Farmer Crop Advisory** | *"Can I spray pesticide on cotton crops in Nagpur today?"* | `get_crop_advisory` |
| **Severe Alerts** | *"Simulate extreme cyclone alert test for Chennai"* | `get_severe_alerts` |
| **Climate Trend** | *"Compare Delhi temperature today vs historical climate"* | `get_historical_climate` |
| **Multilingual (Hindi)** | *"वाराणसी में आज का मौसम कैसा है?"* | `get_current_weather` (Hindi response) |

---

## 📄 License
This project was developed for the **Capabl Agentic AI Hackathon 2026** under the MIT License.
