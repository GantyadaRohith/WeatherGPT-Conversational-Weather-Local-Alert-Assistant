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
| **9** | **Database Persistence (MongoDB)** | **MongoDB Atlas / local MongoDB** via `motor` with zero-crash **Persistent JSON Document Store** fallback (`weathergpt_db.json`) for saved locations, alert dispatch history, and community subscribers. |
| **10** | **Twilio & WhatsApp Cloud API** | Multi-channel disaster alerts via **Meta WhatsApp Cloud API** & **Twilio SMS/WhatsApp**, plus a **Live Evaluator Simulator** with realistic delivery receipts (`✓ Delivered`). |
| **11** | **Scheduled Alert Watchdog** | Automated 60-second background watchdog periodically evaluating saved locations against meteorological thresholds and dispatching warnings. |
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


---

## 🌐 Cloud Production Deployment Guide (Vercel + Render + MongoDB Atlas)

WeatherGPT is designed for modular, decoupled production deployment:
- **Frontend**: [Vercel](https://vercel.com/) (React 19 + Vite + Glassmorphism)
- **Backend**: [Render](https://render.com/) (FastAPI + LangGraph + Uvicorn)
- **Database**: [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (M0 Free Cloud Cluster)

---

### Step 1: Set up MongoDB Atlas (Cloud Database)
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas) and create/sign in to your account.
2. Click **Create Deployment** and choose the **M0 Shared (Free)** tier.
3. **Database User**: Create a username and password (e.g. `weather_admin` and a secure password).
4. **Network Access**: Under Security → Network Access, click **Add IP Address** and choose **Allow Access From Anywhere (`0.0.0.0/0`)**. *(This is required so Render's cloud servers can connect to your database)*.
5. Click **Connect** → **Drivers** (Python):
   Copy your connection URI:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/weathergpt?retryWrites=true&w=majority
   ```

---

### Step 2: Deploy Backend to Render
1. Go to [render.com](https://render.com/) and sign in with GitHub.
2. Click **New +** → **Web Service** → Select your repository:
   `WeatherGPT-Conversational-Weather-Local-Alert-Assistant`
3. Configure the settings:
   - **Name**: `weathergpt-backend`
   - **Root Directory**: `weathergpt`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Under **Environment Variables**, add:
   - `WEATHER_LLM_PROVIDER` = `groq`
   - `GROQ_API_KEY` = *your Groq API key*
   - `GROQ_MODEL` = `openai/gpt-oss-20b`
   - `MONGODB_URI` = *your MongoDB Atlas URI from Step 1*
   - `MONGODB_DB` = `weathergpt`
   - *(Optional Twilio keys)* `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
5. Click **Deploy Web Service**.
   Render will build the service and give you a public URL:
   👉 **`https://your-service-name.onrender.com`**
   *(Test that it is live by opening `https://your-service-name.onrender.com/health`)*.

---

### Step 3: Deploy Frontend to Vercel
1. Go to [vercel.com](https://vercel.com/) and sign in with GitHub.
2. Click **Add New...** → **Project** → Import your repository.
3. In the project configuration:
   - **Root Directory**: Click *Edit* and select **`weathergpt/react_frontend`**.
   - **Framework Preset**: `Vite` (auto-detected).
4. Under **Environment Variables**, add:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: Your live Render backend URL from Step 2:
     `https://your-service-name.onrender.com` *(do not add trailing slash)*
5. Click **Deploy**!
   Vercel will build the frontend and give you a live production link:
   👉 **`https://your-app-name.vercel.app`**

## 📄 License
This project was developed for the **Capabl Agentic AI Hackathon 2026** under the MIT License.
