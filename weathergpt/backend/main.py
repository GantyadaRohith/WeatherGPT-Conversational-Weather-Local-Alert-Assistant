"""
main.py
FastAPI backend server for WeatherGPT.
Supports:
- Multi-Agent LangGraph/Hybrid reasoning agent
- Fixed location weather hero widget (Apple Weather style)
- Unified MongoDB and Persistent JSON Document Store database layer
- Twilio SMS, Twilio WhatsApp, Meta WhatsApp Cloud API & Live Evaluator Simulator
- Automated Scheduled Watchdog alerting for saved locations
- Static web hosting for React 19 production bundle
"""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agent import WeatherAgent
from backend.weather_tools import (
    fetch_current_weather,
    fetch_forecast_weather,
    fetch_historical_climate,
    fetch_past_weather,
    geocode_location,
    reverse_geocode_coords
)
from backend.advisories import rank_best_crops_for_weather
from backend.alerts import check_extreme_weather_alerts, simulate_extreme_scenario
from backend.llm_client import llm_client, LLM_CONFIG
from backend.database import db_manager
from backend.notifications import notification_manager


# Watchdog evaluation worker
async def run_watchdog_evaluation(auto_dispatch: bool = False) -> List[Dict[str, Any]]:
    """Runs automated meteorological threshold evaluation across all saved locations."""
    saved = await db_manager.get_saved_locations()
    results = []

    for item in saved:
        loc_name = item.get("location")
        phone = item.get("phone") or "+919876543210"
        channel = item.get("channel") or "whatsapp"
        thresh_rain = item.get("threshold_rain_mm", 25.0)

        try:
            curr = await fetch_current_weather(loc_name)
            fore = await fetch_forecast_weather(loc_name, days=2)
            alerts = check_extreme_weather_alerts(curr, fore)

            # Custom threshold check
            cur_rain = curr.get("precipitation", 0.0)
            if cur_rain >= thresh_rain:
                alerts.append({
                    "severity": "ORANGE",
                    "type": f"Rainfall Threshold Breached (>{thresh_rain}mm)",
                    "message": f"Recorded rainfall of {cur_rain}mm exceeded user threshold of {thresh_rain}mm in {loc_name}.",
                    "action": "Initiate drainage protocols and protect unharvested crops."
                })

            dispatches = []
            if alerts and auto_dispatch:
                # Dispatch alert for each active hazard
                for al in alerts:
                    disp = await notification_manager.dispatch_alert(
                        location=loc_name,
                        alert=al,
                        recipient_phone=phone,
                        channel=channel
                    )
                    dispatches.append(disp)
                await db_manager.update_location_alert_time(loc_name)

            results.append({
                "location": loc_name,
                "current_temp": curr.get("temperature"),
                "rain_prob": fore["daily_forecast"][0].get("precip_prob", 0) if fore.get("daily_forecast") else 0,
                "precipitation": cur_rain,
                "phone": phone,
                "channel": channel,
                "active_alerts": alerts,
                "dispatches": dispatches
            })
        except Exception as e:
            results.append({"location": loc_name, "error": str(e), "active_alerts": []})

    return results


async def scheduled_watchdog_task():
    """Background loop that periodically evaluates saved locations and dispatches alerts."""
    while True:
        try:
            await asyncio.sleep(60)  # Check every 60 seconds
            await run_watchdog_evaluation(auto_dispatch=True)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[WatchdogTask] Background check error: {e}")
            await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Database (MongoDB with JSON document store fallback)
    await db_manager.initialize()

    # Seed initial demo locations if empty
    locs = await db_manager.get_saved_locations()
    if not locs:
        await db_manager.add_saved_location(
            "Visakhapatnam",
            threshold_rain_mm=20.0,
            notify_heatwave=True,
            phone="+919876543210",
            channel="whatsapp"
        )
        await db_manager.add_saved_location(
            "Nagpur",
            threshold_rain_mm=25.0,
            notify_heatwave=True,
            phone="+919876543210",
            channel="sms"
        )

    # Start scheduled alert watchdog
    watchdog_worker = asyncio.create_task(scheduled_watchdog_task())
    yield
    # Cleanup
    watchdog_worker.cancel()


app = FastAPI(
    title="WeatherGPT - Conversational Weather & Local Alert Assistant",
    description="Agentic AI Hackathon Prototype (Track A · A2) with React Frontend, MongoDB, Twilio/WhatsApp, and Multi-Agent LLMs",
    version="2.1.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = WeatherAgent()


# Request Models
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
    phone: Optional[str] = ""
    channel: Optional[str] = "whatsapp"


class SendNotificationRequest(BaseModel):
    location: str
    alert_type: str = "Severe Weather Alert"
    severity: str = "RED"
    message: str
    action: str
    phone: str = "+919876543210"
    channel: str = "whatsapp"
    simulate: Optional[bool] = False


class NotificationConfigRequest(BaseModel):
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    whatsapp_token: Optional[str] = None
    whatsapp_phone_number_id: Optional[str] = None


class SubscriberRequest(BaseModel):
    name: str
    phone: str
    location: str
    channel: Optional[str] = "whatsapp"


# --- Chat & LLM Endpoints ---
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
    """Returns the current LLM provider and readiness status."""
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


# --- Weather Hero & Tools ---
@app.get("/api/weather/hero")
async def get_fixed_location_hero(city: str = "New Delhi"):
    """Supplies real-time hero metrics, high/low, next 12-hr timeline, and atmospheric telemetry."""
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
    return await fetch_current_weather(city)


@app.get("/api/weather/forecast")
async def get_forecast(city: str = "Delhi", days: int = 7):
    return await fetch_forecast_weather(city, days=days)


@app.get("/api/weather/history")
async def get_history(city: str = "Delhi", years: int = 1):
    return await fetch_historical_climate(city, years_back=years)


@app.get("/api/weather/past")
async def get_past(city: str = "Delhi", days: int = 10):
    return await fetch_past_weather(city, days=days)


@app.get("/api/weather/reverse-geocode")
async def reverse_geocode_endpoint(lat: float, lon: float):
    return await reverse_geocode_coords(lat, lon)


@app.get("/api/advisories/crops/ranking")
async def get_crop_rankings(city: str = "Delhi"):
    curr = await fetch_current_weather(city)
    fore = await fetch_forecast_weather(city, days=3)
    return rank_best_crops_for_weather(curr, fore, top_n=8)


# --- Database & Persistence Endpoints ---
@app.get("/api/database/status")
async def get_database_status():
    """Returns database telemetry, active engine (MongoDB or JSON Document Store), and counts."""
    return await db_manager.get_status()


# --- Saved Locations (Backed by Database) ---
@app.get("/api/saved-locations")
async def list_saved_locations():
    """Lists saved locations being monitored by the alert watchdog from MongoDB / JSON Store."""
    return await db_manager.get_saved_locations()


@app.post("/api/saved-locations")
async def add_saved_location(req: SaveLocationRequest):
    """Adds or updates a location in the active monitoring database."""
    doc = await db_manager.add_saved_location(
        location=req.location,
        threshold_rain_mm=req.threshold_rain_mm or 25.0,
        notify_heatwave=req.notify_heatwave if req.notify_heatwave is not None else True,
        phone=req.phone or "",
        channel=req.channel or "whatsapp"
    )
    return {"status": "success", "message": f"Location {req.location} added to database watchdog.", "data": doc}


@app.delete("/api/saved-locations/{location_name}")
async def delete_saved_location(location_name: str):
    """Removes a location from the monitoring watchdog database."""
    success = await db_manager.delete_saved_location(location_name)
    return {"status": "success" if success else "not_found", "message": f"Processed removal for {location_name}"}


# --- Scheduled Watchdog & Alerts ---
@app.get("/api/alerts/watchdog-check")
async def check_watchdog_alerts():
    """Runs automated watchdog check across all saved locations in the database."""
    return await run_watchdog_evaluation(auto_dispatch=False)


@app.post("/api/alerts/watchdog-dispatch")
async def trigger_watchdog_dispatch():
    """Forces an immediate check & alert dispatch evaluation for all saved locations."""
    return await run_watchdog_evaluation(auto_dispatch=True)


@app.post("/api/alerts/simulate")
async def trigger_simulation(scenario: str = "cyclone", city: str = "Coastal Hub"):
    """Simulates severe hazard scenario for judges."""
    return simulate_extreme_scenario(scenario, city=city)


# --- Notification System Endpoints (Twilio & WhatsApp Cloud API) ---
@app.get("/api/notifications/status")
async def get_notification_status():
    """Returns status of Twilio SMS, WhatsApp, and Cloud API channels."""
    return notification_manager.get_status()


@app.post("/api/notifications/config")
async def update_notification_config(req: NotificationConfigRequest):
    """Updates runtime Twilio and WhatsApp credentials."""
    notification_manager.update_config(req.dict(exclude_unset=True))
    return {"status": "success", "message": "Notification credentials updated."}


@app.post("/api/notifications/send")
async def send_notification_endpoint(req: SendNotificationRequest):
    """
    Direct endpoint to dispatch an urgent alert via WhatsApp or Twilio SMS.
    Logs dispatch to MongoDB / persistent JSON document store.
    """
    alert_payload = {
        "severity": req.severity,
        "type": req.alert_type,
        "message": req.message,
        "action": req.action
    }
    result = await notification_manager.dispatch_alert(
        location=req.location,
        alert=alert_payload,
        recipient_phone=req.phone,
        channel=req.channel,
        force_simulation=req.simulate
    )
    return {"status": "success", "data": result}


@app.get("/api/notifications/dispatches")
async def get_dispatch_history(limit: int = 50):
    """Fetches historical alert dispatches stored in MongoDB / persistent JSON store."""
    records = await db_manager.get_alert_dispatches(limit=limit)
    return {"status": "success", "count": len(records), "dispatches": records}


# --- Subscriber Management Endpoints ---
@app.get("/api/subscribers")
async def get_subscribers():
    """Retrieves all registered community subscribers from the database."""
    subs = await db_manager.get_subscribers()
    return {"status": "success", "count": len(subs), "subscribers": subs}


@app.post("/api/subscribers")
async def register_subscriber(req: SubscriberRequest):
    """Registers a citizen/farmer for proactive WhatsApp or SMS weather advisories."""
    sub = await db_manager.add_subscriber(
        name=req.name,
        phone=req.phone,
        location=req.location,
        channel=req.channel or "whatsapp"
    )
    return {"status": "success", "message": f"Subscribed {req.name} for {req.channel.upper()} alerts.", "subscriber": sub}


@app.delete("/api/subscribers/{phone}")
async def remove_subscriber(phone: str):
    """Removes a subscriber from the alerts database."""
    success = await db_manager.delete_subscriber(phone)
    return {"status": "success" if success else "not_found", "message": f"Removed subscriber with phone {phone}"}


# --- Health Check Endpoint (Render Production Monitoring) ---
@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint for Render / cloud monitoring."""
    db_stat = await db_manager.get_status()
    notif_stat = notification_manager.get_status()
    return {
        "status": "healthy",
        "service": "WeatherGPT API Gateway",
        "version": "2.1.0",
        "database": db_stat,
        "notifications": notif_stat
    }


# --- Static Frontend Serving & Cloud Fallback ---
react_dist = os.path.join(os.path.dirname(__file__), "..", "react_frontend", "dist")
legacy_frontend = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.exists(react_dist):
    app.mount("/", StaticFiles(directory=react_dist, html=True), name="react_frontend")
elif os.path.exists(legacy_frontend):
    app.mount("/", StaticFiles(directory=legacy_frontend, html=True), name="frontend")
else:
    @app.get("/")
    async def root_gateway():
        return {
            "service": "WeatherGPT API Gateway (Render Production)",
            "status": "online",
            "docs": "/docs",
            "health": "/health",
            "database_status": "/api/database/status",
            "message": "Backend API is live. Connect your Vercel frontend via VITE_API_BASE_URL."
        }

