"""
main.py
FastAPI backend server for WeatherGPT.
Supports LLM configuration, fixed location weather hero widget,
multi-agent chat endpoint, and static web hosting.
"""

import os
from dotenv import load_dotenv

load_dotenv()
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agent import WeatherAgent
from backend.weather_tools import (
    fetch_current_weather,
    fetch_forecast_weather,
    fetch_historical_climate,
    geocode_location
)
from backend.alerts import (
    SAVED_LOCATIONS,
    check_extreme_weather_alerts,
    simulate_extreme_scenario
)
from backend.llm_client import llm_client, LLM_CONFIG

app = FastAPI(
    title="WeatherGPT - Conversational Weather & Local Alert Assistant",
    description="Agentic AI Hackathon Prototype (Track A · A2) with React Frontend and Multi-Agent LLMs",
    version="2.0.0"
)

# Enable CORS for local Vite dev server (http://localhost:5173) and any port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = WeatherAgent()


class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "en"
    fixed_location: Optional[str] = None


class LLMConfigRequest(BaseModel):
    provider: str  # "local", "groq", "gemini", "openai"
    api_key: Optional[str] = None
    model: Optional[str] = None


class SaveLocationRequest(BaseModel):
    location: str
    threshold_rain_mm: Optional[float] = 25.0
    notify_heatwave: Optional[bool] = True


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Processes user query through Multi-Agent WeatherAgent with full tool-selection trace."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    response = await agent.run(
        req.message,
        language=req.language or "en",
        fixed_location=req.fixed_location
    )
    return response


@app.get("/api/config/llm")
async def get_llm_config():
    """Returns the current LLM provider and readiness status (without exposing full secret keys)."""
    prov = llm_client.config["provider"]
    has_key = bool(
        (prov == "groq" and llm_client.config.get("groq_api_key")) or
        (prov == "gemini" and llm_client.config.get("gemini_api_key")) or
        (prov == "openai" and llm_client.config.get("openai_api_key")) or
        prov == "local"
    )
    return {
        "provider": prov,
        "is_ready": has_key,
        "models": {
            "groq": llm_client.config.get("groq_model"),
            "gemini": llm_client.config.get("gemini_model"),
            "openai": llm_client.config.get("openai_model")
        }
    }


@app.post("/api/config/llm")
async def set_llm_config(req: LLMConfigRequest):
    """Updates runtime LLM provider and keys."""
    llm_client.update_config(provider=req.provider, api_key=req.api_key, model=req.model)
    return {
        "status": "success",
        "message": f"Switched to {req.provider} engine.",
        "provider": req.provider
    }


@app.get("/api/weather/hero")
async def get_fixed_location_hero(city: str = "New Delhi"):
    """
    Fixed Location Hero Endpoint (Apple Weather Style):
    Supplies real-time hero metrics, high/low, next 12-hr timeline, and atmospheric telemetry.
    """
    try:
        curr = await fetch_current_weather(city)
        fore = await fetch_forecast_weather(city, days=3)
        alerts = check_extreme_weather_alerts(curr, fore)

        hourly_items = []
        if fore and "hourly_chart" in fore:
            hours = fore["hourly_chart"]["hours"][:12]
            temps = fore["hourly_chart"]["temperatures"][:12]
            rains = fore["hourly_chart"]["rain_probabilities"][:12]
            for h, t, r in zip(hours, temps, rains):
                hourly_items.append({
                    "time": h,
                    "temp": round(t),
                    "rain_prob": r,
                    "icon": "🌧️" if r > 50 else ("⛅" if curr.get("condition") == "Partly cloudy" else "☀️")
                })

        return {
            "location": curr.get("location"),
            "current": curr,
            "daily_high": curr.get("temp_max"),
            "daily_low": curr.get("temp_min"),
            "hourly_timeline": hourly_items,
            "alerts": alerts,
            "air_quality_summary": "Moderate / Normal",
            "uv_category": "Very High" if curr.get("uv_index", 0) > 8 else ("High" if curr.get("uv_index", 0) > 5 else "Moderate")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weather/current")
async def get_current(city: str = "Delhi"):
    """Fetches real-time weather observations."""
    return await fetch_current_weather(city)


@app.get("/api/weather/forecast")
async def get_forecast(city: str = "Delhi", days: int = 7):
    """Fetches 7-day forecast and 24-hr hourly snapshot."""
    return await fetch_forecast_weather(city, days=days)


@app.get("/api/weather/history")
async def get_history(city: str = "Delhi", years: int = 1):
    """Fetches historical climate anomaly comparison."""
    return await fetch_historical_climate(city, years_back=years)


@app.get("/api/saved-locations")
async def list_saved_locations():
    """Lists saved locations being monitored by the alert watchdog."""
    return list(SAVED_LOCATIONS.values())


@app.post("/api/saved-locations")
async def add_saved_location(req: SaveLocationRequest):
    """Adds a location to the active monitoring watchdog."""
    SAVED_LOCATIONS[req.location.title()] = {
        "location": req.location.title(),
        "threshold_rain_mm": req.threshold_rain_mm,
        "notify_heatwave": req.notify_heatwave,
        "created_at": "Active"
    }
    return {"status": "success", "message": f"Location {req.location} added to alert watchdog."}


@app.delete("/api/saved-locations/{location_name}")
async def delete_saved_location(location_name: str):
    """Removes a location from the monitoring watchdog."""
    if location_name.title() in SAVED_LOCATIONS:
        del SAVED_LOCATIONS[location_name.title()]
    return {"status": "success", "message": f"Removed {location_name}"}


@app.get("/api/alerts/watchdog-check")
async def check_watchdog_alerts():
    """Runs automated watchdog check across all saved locations."""
    results = []
    for loc_name, cfg in SAVED_LOCATIONS.items():
        try:
            curr = await fetch_current_weather(loc_name)
            fore = await fetch_forecast_weather(loc_name, days=2)
            alerts = check_extreme_weather_alerts(curr, fore)
            results.append({
                "location": loc_name,
                "current_temp": curr.get("temperature"),
                "rain_prob": fore["daily_forecast"][0].get("precip_prob", 0) if fore.get("daily_forecast") else 0,
                "active_alerts": alerts
            })
        except Exception as e:
            results.append({"location": loc_name, "error": str(e), "active_alerts": []})
    return results


@app.post("/api/alerts/simulate")
async def trigger_simulation(scenario: str = "cyclone", city: str = "Coastal Hub"):
    """Simulates severe hazard scenario for judges."""
    return simulate_extreme_scenario(scenario, city=city)


# Mount static frontend: prioritizes react_frontend/dist if built, else fallback frontend
react_dist = os.path.join(os.path.dirname(__file__), "..", "react_frontend", "dist")
legacy_frontend = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.exists(react_dist):
    app.mount("/", StaticFiles(directory=react_dist, html=True), name="react_frontend")
elif os.path.exists(legacy_frontend):
    app.mount("/", StaticFiles(directory=legacy_frontend, html=True), name="frontend")
