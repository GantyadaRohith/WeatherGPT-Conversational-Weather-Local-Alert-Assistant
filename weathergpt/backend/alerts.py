"""
alerts.py
Extreme weather alerts, proactive threshold monitoring,
and scheduled saved-location alert watchdog.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

# In-memory saved locations store for user's alert monitoring
SAVED_LOCATIONS: Dict[str, Dict[str, Any]] = {
    "Varanasi": {"location": "Varanasi", "threshold_rain_mm": 20, "notify_heatwave": True, "created_at": "2026-09-19"},
    "Mumbai": {"location": "Mumbai", "threshold_rain_mm": 35, "notify_heatwave": False, "created_at": "2026-09-19"},
    "Jaipur": {"location": "Jaipur", "threshold_rain_mm": 15, "notify_heatwave": True, "created_at": "2026-09-19"}
}


def check_extreme_weather_alerts(weather: Dict[str, Any], forecast: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Evaluates meteorological readings against national meteorological safety thresholds."""
    alerts = []
    temp = weather.get("temperature", 25.0)
    wind = weather.get("wind_speed", 10.0)
    rain = weather.get("precipitation", 0.0)
    code = weather.get("weather_code", 0)
    city = weather.get("location", {}).get("name", "Current Area")

    # 1. Heatwave Alert
    if temp >= 43.0:
        alerts.append({
            "severity": "RED",
            "type": "Severe Heatwave Warning",
            "message": f"Extreme dangerous heat recorded at {temp}°C in {city}. High risk of sunstroke. Red alert issued.",
            "action": "Stay indoors, avoid outdoor exertion, drink ORS/lemon water regularly."
        })
    elif temp >= 39.5:
        alerts.append({
            "severity": "ORANGE",
            "type": "Heatwave Advisory",
            "message": f"High temperatures ({temp}°C) in {city}. Vulnerable groups should avoid midday sun.",
            "action": "Stay hydrated and avoid direct sun between 11 AM and 4 PM."
        })

    # 2. Heavy Rainfall / Flash Flood Risk
    daily = forecast.get("daily_forecast", []) if forecast else []
    max_forecast_rain = max([d.get("precip_sum", 0) for d in daily[:2]]) if daily else 0
    max_rain_prob = max([d.get("precip_prob", 0) for d in daily[:2]]) if daily else 0

    if rain >= 50.0 or max_forecast_rain >= 55.0:
        alerts.append({
            "severity": "RED",
            "type": "Flash Flood & Torrential Rain Alert",
            "message": f"Extremely heavy precipitation ({rain or max_forecast_rain} mm) detected in {city}.",
            "action": "Avoid underpasses, keep emergency battery lamps ready, evacuate low-lying banks if instructed."
        })
    elif rain >= 20.0 or max_forecast_rain >= 25.0 or max_rain_prob >= 80:
        alerts.append({
            "severity": "YELLOW",
            "type": "Heavy Rain & Waterlogging Advisory",
            "message": f"Significant rainfall expected ({max_forecast_rain or rain} mm, {max_rain_prob}% probability) in {city}.",
            "action": "Commuters should anticipate localized traffic delays and waterlogging."
        })

    # 3. High Gale / Cyclonic Winds
    if wind >= 60.0:
        alerts.append({
            "severity": "RED",
            "type": "Cyclonic Gale Warning",
            "message": f"Dangerous destructive winds of {wind} km/h detected in {city}.",
            "action": "Secure outdoor sheds, stay clear of electric poles and old trees."
        })
    elif wind >= 40.0:
        alerts.append({
            "severity": "YELLOW",
            "type": "Squall / High Wind Advisory",
            "message": f"Strong gusty winds ({wind} km/h) active across {city}.",
            "action": "Drive high-profile vehicles with care and tie down loose roof sheets."
        })

    # 4. Severe Thunderstorm / Hailstorm
    if code in [95, 96, 99]:
        alerts.append({
            "severity": "ORANGE",
            "type": "Severe Thunderstorm & Lightning Warning",
            "message": f"Active thunderstorm with possible hail activity detected in {city} airspace.",
            "action": "Do not take shelter under solitary trees or open tin sheds. Unplug sensitive electrical devices."
        })

    # 5. Cold Wave
    if temp <= 4.0:
        alerts.append({
            "severity": "ORANGE",
            "type": "Severe Cold Wave & Ground Frost Warning",
            "message": f"Near-freezing temperatures ({temp}°C) in {city}. Risk of ground frost for standing crops.",
            "action": "Give light irrigation to protect mustard and potato crops from frost injury."
        })

    return alerts


def simulate_extreme_scenario(scenario_type: str, city: str = "Coastal Hub") -> Dict[str, Any]:
    """Provides a deterministic extreme weather simulation for hackathon judges demonstration."""
    scenarios = {
        "cyclone": {
            "severity": "RED",
            "type": "Severe Cyclonic Storm Warning (Cyclone Vayu)",
            "message": f"Deep depression intensifying into a severe cyclonic storm approaching {city}. Sustained winds 85-105 km/h with tidal surges.",
            "action": "Fishermen strictly advised not to venture into sea. Coastal residents relocate to shelter centres.",
            "metrics": {"temp": 26.2, "wind": 92.5, "rain": 115.0, "icon": "🌪️"}
        },
        "cloudburst": {
            "severity": "RED",
            "type": "Torrential Downpour & Cloudburst Alert",
            "message": f"Rapid cloudburst activity over {city} drainage basin. 80mm rainfall recorded within 90 minutes.",
            "action": "Avoid waterlogged subways. District disaster management force activated.",
            "metrics": {"temp": 22.0, "wind": 45.0, "rain": 82.0, "icon": "⛈️"}
        },
        "heatwave": {
            "severity": "RED",
            "type": "Extreme Heatwave Red Alert (Loo Warning)",
            "message": f"Severe heatwave conditions persisting across {city}. Peak daytime temperature reached 45.8°C with dry westerly winds.",
            "action": "Do not step out between 12 PM and 4 PM. Keep animals hydrated in shaded enclosures.",
            "metrics": {"temp": 45.8, "wind": 22.0, "rain": 0.0, "icon": "🔥"}
        }
    }
    return scenarios.get(scenario_type.lower(), scenarios["cyclone"])
