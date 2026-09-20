"""
advisories.py
Generates contextual agricultural crop advisories for Indian farmers
and commuter/travel advisories based on meteorological metrics.
"""

from typing import Any, Dict, List

CROP_PROFILES = {
    "wheat": {
        "name": "Wheat (गेहूं)",
        "ideal_temp": (15, 25),
        "rain_sensitive_stages": ["flowering", "grain filling", "harvesting"],
        "advice_dry": "Maintain light irrigation during crown root initiation and flowering. Avoid heavy watering.",
        "advice_wet": "High humidity may trigger rust/powdery mildew. Delay pesticide spray until foliage dries."
    },
    "rice": {
        "name": "Paddy / Rice (धान)",
        "ideal_temp": (22, 35),
        "rain_sensitive_stages": ["tillering", "panicle initiation"],
        "advice_dry": "Ensure 3-5 cm standing water during panicle stage. Prioritize canal/pump irrigation.",
        "advice_wet": "Rain is favorable for paddy. Open field drainage channels to prevent excessive submergence."
    },
    "cotton": {
        "name": "Cotton (कपास)",
        "ideal_temp": (21, 35),
        "rain_sensitive_stages": ["boll opening", "picking"],
        "advice_dry": "Scout for sucking pests (whitefly/thrips) in dry warm weather. Maintain optimum soil moisture.",
        "advice_wet": "Continuous rain during boll opening can damage fiber quality. Halt picking until dry sunny spells."
    },
    "mustard": {
        "name": "Mustard (सरसों)",
        "ideal_temp": (15, 25),
        "rain_sensitive_stages": ["pod development"],
        "advice_dry": "Irrigate at pod filling stage. Watch for aphid infestation if overcast conditions persist.",
        "advice_wet": "Cloudy and wet conditions increase aphid spread. Spray recommended neem-based bio-pesticide when clear."
    },
    "vegetables": {
        "name": "Vegetables & Horticulture (सब्जियां)",
        "ideal_temp": (18, 30),
        "rain_sensitive_stages": ["all"],
        "advice_dry": "Mulch beds to conserve soil moisture. Drip irrigate in early mornings or evenings.",
        "advice_wet": "Provide staking/support to tomato and climber vines. Clear excess drainage to prevent root rot."
    }
}


def generate_crop_advisory(
    weather: Dict[str, Any],
    forecast: Dict[str, Any],
    crop_name: str = "general"
) -> Dict[str, Any]:
    """Generates an actionable agricultural advisory for farmers."""
    temp = weather.get("temperature", 28.0)
    humidity = weather.get("humidity", 60)
    wind = weather.get("wind_speed", 10.0)
    rain_current = weather.get("precipitation", 0.0)
    
    # Check rain in upcoming 3 days
    daily = forecast.get("daily_forecast", [])[:3]
    rain_upcoming_max = max([d.get("precip_prob", 0) for d in daily]) if daily else 0
    total_rain_expected = sum([d.get("precip_sum", 0) for d in daily]) if daily else 0

    crop_key = crop_name.lower().strip()
    profile = CROP_PROFILES.get(crop_key, {
        "name": "General Agricultural Crops",
        "ideal_temp": (18, 32),
        "advice_dry": "Monitor soil moisture regularly and schedule irrigation in evening hours.",
        "advice_wet": "Clear field ditches to prevent waterlogging around root zones."
    })

    # Pesticide / Chemical Spray Feasibility
    spray_allowed = True
    spray_reasons = []
    if wind > 18.0:
        spray_allowed = False
        spray_reasons.append(f"High wind speed ({wind} km/h) causes chemical drift.")
    if rain_upcoming_max > 45 or rain_current > 0.5 or total_rain_expected > 5.0:
        spray_allowed = False
        spray_reasons.append(f"Rain likelihood is {rain_upcoming_max}% ({round(total_rain_expected, 1)}mm expected) which washes off foliar sprays.")
    if temp > 38.0:
        spray_allowed = False
        spray_reasons.append(f"Extreme heat ({temp}°C) causes rapid evaporation and leaf scorching.")

    # Irrigation Recommendation
    if total_rain_expected > 15.0 or rain_upcoming_max > 70:
        irrigation_rec = "POSTPONE IRRIGATION: Substantial precipitation is forecast over the next 48-72 hours. Conserve water and power."
        irrigation_badge = "Postpone"
    elif temp > 35.0 and total_rain_expected < 2.0:
        irrigation_rec = "IMMEDIATE IRRIGATION RECOMMENDED: High evaporation demand and temperature stress. Irrigate during night or early morning."
        irrigation_badge = "Irrigate"
    else:
        irrigation_rec = "NORMAL SCHEDULE: Maintain regular moisture check. No adverse weather disruptions expected."
        irrigation_badge = "Normal"

    # Specific crop guidance
    crop_specific_tip = profile.get("advice_wet") if total_rain_expected > 10.0 else profile.get("advice_dry")

    return {
        "crop": profile["name"],
        "irrigation_action": irrigation_badge,
        "irrigation_details": irrigation_rec,
        "spray_feasible": spray_allowed,
        "spray_guidance": "SAFE TO SPRAY: Winds are calm and no rain is predicted." if spray_allowed else "DO NOT SPRAY: " + " ".join(spray_reasons),
        "crop_tip": crop_specific_tip,
        "summary": f"Advisory for {profile['name']} at {weather['location']['name']}: {irrigation_badge} irrigation status. Spraying is {'PERMITTED' if spray_allowed else 'RESTRICTED'}."
    }


def generate_commuter_advisory(weather: Dict[str, Any], forecast: Dict[str, Any]) -> Dict[str, Any]:
    """Generates daily travel, commuting, and health advisories."""
    temp = weather.get("temperature", 28.0)
    condition = weather.get("condition", "Clear")
    wind = weather.get("wind_speed", 10.0)
    precip = weather.get("precipitation", 0.0)
    uv = weather.get("uv_index", 3)

    daily = forecast.get("daily_forecast", [])[:1]
    rain_prob = daily[0].get("precip_prob", 10) if daily else 10

    alerts = []
    if rain_prob > 60 or precip > 2.0:
        alerts.append("Carry an umbrella / raincoat. Wet roads may cause commute delays and localized waterlogging.")
    if temp > 38.0:
        alerts.append("High heat caution: Stay hydrated and avoid prolonged outdoor travel between 12:00 PM and 3:30 PM.")
    elif temp < 8.0:
        alerts.append("Cold wave caution: Morning fog may reduce highway visibility. Wear layered thermal clothing.")
    if uv > 7:
        alerts.append("High UV index: Sun protection recommended (sunglasses, hat, sunscreen).")
    if wind > 35:
        alerts.append("Gusty winds: Drive two-wheelers cautiously on open flyovers and highways.")

    if not alerts:
        alerts.append("Favorable outdoor conditions: Great weather for travel and outdoor activities.")

    return {
        "status": "Warning" if len(alerts) > 1 and ("caution" in "".join(alerts) or "umbrella" in "".join(alerts)) else "Good",
        "advisories": alerts,
        "commute_score": "Fair" if rain_prob > 50 or temp > 38 else "Excellent"
    }
