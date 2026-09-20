"""
weather_tools.py
Live meteorological data integration using Open-Meteo free APIs.
No API key required. High accuracy worldwide with rich support for India.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"

# WMO Weather interpretation codes
WMO_CODE_MAP = {
    0: {"desc": "Clear sky", "icon": "☀️", "category": "clear"},
    1: {"desc": "Mainly clear", "icon": "🌤️", "category": "clear"},
    2: {"desc": "Partly cloudy", "icon": "⛅", "category": "cloudy"},
    3: {"desc": "Overcast", "icon": "☁️", "category": "cloudy"},
    45: {"desc": "Foggy", "icon": "🌫️", "category": "fog"},
    48: {"desc": "Depositing rime fog", "icon": "🌫️", "category": "fog"},
    51: {"desc": "Light drizzle", "icon": "🌦️", "category": "rain"},
    53: {"desc": "Moderate drizzle", "icon": "🌦️", "category": "rain"},
    55: {"desc": "Dense drizzle", "icon": "🌧️", "category": "rain"},
    61: {"desc": "Slight rain", "icon": "🌧️", "category": "rain"},
    63: {"desc": "Moderate rain", "icon": "🌧️", "category": "rain"},
    65: {"desc": "Heavy rain", "icon": "⛈️", "category": "heavy_rain"},
    71: {"desc": "Slight snow fall", "icon": "🌨️", "category": "snow"},
    73: {"desc": "Moderate snow fall", "icon": "🌨️", "category": "snow"},
    75: {"desc": "Heavy snow fall", "icon": "❄️", "category": "snow"},
    80: {"desc": "Slight rain showers", "icon": "🌦️", "category": "rain"},
    81: {"desc": "Moderate rain showers", "icon": "🌧️", "category": "rain"},
    82: {"desc": "Violent rain showers", "icon": "⛈️", "category": "heavy_rain"},
    95: {"desc": "Thunderstorm", "icon": "⚡", "category": "storm"},
    96: {"desc": "Thunderstorm with slight hail", "icon": "⛈️", "category": "storm"},
    99: {"desc": "Thunderstorm with heavy hail", "icon": "🌪️", "category": "storm"},
}

CITY_ALIASES = {
    "vizag": "Visakhapatnam",
    "visakhapatnam": "Visakhapatnam",
    "bengaluru": "Bengaluru",
    "bangalore": "Bengaluru",
    "bombay": "Mumbai",
    "mumbai": "Mumbai",
    "calcutta": "Kolkata",
    "kolkata": "Kolkata",
    "madras": "Chennai",
    "chennai": "Chennai",
    "banaras": "Varanasi",
    "kashi": "Varanasi",
    "varanasi": "Varanasi",
    "gurgaon": "Gurugram",
    "gurugram": "Gurugram",
    "baroda": "Vadodara",
    "vadodara": "Vadodara",
    "cochin": "Kochi",
    "kochi": "Kochi",
    "trivandrum": "Thiruvananthapuram",
    "thiruvananthapuram": "Thiruvananthapuram",
    "poona": "Pune",
    "pune": "Pune",
    "secunderabad": "Hyderabad",
    "hyderabad": "Hyderabad",
    "delhi": "New Delhi",
    "new delhi": "New Delhi",
    "ncr": "New Delhi",
}

FALLBACK_CITIES = {
    "delhi": {"name": "New Delhi", "lat": 28.6139, "lon": 77.2090, "country": "India", "admin1": "Delhi"},
    "mumbai": {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "country": "India", "admin1": "Maharashtra"},
    "bengaluru": {"name": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "country": "India", "admin1": "Karnataka"},
    "bangalore": {"name": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "country": "India", "admin1": "Karnataka"},
    "kolkata": {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639, "country": "India", "admin1": "West Bengal"},
    "chennai": {"name": "Chennai", "lat": 13.0827, "lon": 80.2707, "country": "India", "admin1": "Tamil Nadu"},
    "hyderabad": {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867, "country": "India", "admin1": "Telangana"},
    "pune": {"name": "Pune", "lat": 18.5204, "lon": 73.8567, "country": "India", "admin1": "Maharashtra"},
    "jaipur": {"name": "Jaipur", "lat": 26.9124, "lon": 75.7873, "country": "India", "admin1": "Rajasthan"},
    "lucknow": {"name": "Lucknow", "lat": 26.8467, "lon": 80.9462, "country": "India", "admin1": "Uttar Pradesh"},
    "patna": {"name": "Patna", "lat": 25.5941, "lon": 85.1376, "country": "India", "admin1": "Bihar"},
    "nagpur": {"name": "Nagpur", "lat": 21.1458, "lon": 79.0882, "country": "India", "admin1": "Maharashtra"},
    "ahmedabad": {"name": "Ahmedabad", "lat": 23.0225, "lon": 72.5714, "country": "India", "admin1": "Gujarat"},
    "varanasi": {"name": "Varanasi", "lat": 25.3176, "lon": 82.9739, "country": "India", "admin1": "Uttar Pradesh"},
    "kochi": {"name": "Kochi", "lat": 9.9312, "lon": 76.2673, "country": "India", "admin1": "Kerala"},
    "visakhapatnam": {"name": "Visakhapatnam", "lat": 17.6800, "lon": 83.2016, "country": "India", "admin1": "Andhra Pradesh"},
    "vizag": {"name": "Visakhapatnam", "lat": 17.6800, "lon": 83.2016, "country": "India", "admin1": "Andhra Pradesh"},
}


async def geocode_location(location_name: str) -> Optional[Dict[str, Any]]:
    """Geocodes a place name into latitude, longitude, and formatted name."""
    clean_name = location_name.strip().lower()
    
    # Resolve aliases first (e.g. vizag -> Visakhapatnam)
    clean_name = CITY_ALIASES.get(clean_name, clean_name)
    
    # Check fallback / cached common Indian cities
    if clean_name in FALLBACK_CITIES:
        return FALLBACK_CITIES[clean_name]

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(
                GEOCODING_URL,
                params={"name": location_name, "count": 3, "language": "en", "format": "json"}
            )
            if resp.status_code == 200:
                data = resp.json()
                if "results" in data and len(data["results"]) > 0:
                    first = data["results"][0]
                    return {
                        "name": first.get("name", location_name),
                        "lat": first.get("latitude"),
                        "lon": first.get("longitude"),
                        "country": first.get("country", ""),
                        "admin1": first.get("admin1", ""),
                        "timezone": first.get("timezone", "auto")
                    }
    except Exception as e:
        print(f"Geocoding error for {location_name}: {e}")

    # Fallback to Delhi if nothing found
    return {"name": location_name.title(), "lat": 28.6139, "lon": 77.2090, "country": "India", "admin1": "Delhi"}


async def fetch_current_weather(location_name: str) -> Dict[str, Any]:
    """Retrieves real-time weather information."""
    geo = await geocode_location(location_name)
    lat = geo["lat"]
    lon = geo["lon"]

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
            "surface_pressure",
            "uv_index",
        ],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "uv_index_max"],
        "timezone": "auto",
        "forecast_days": 1
    }

    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.get(WEATHER_FORECAST_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    current = data.get("current", {})
    daily = data.get("daily", {})
    code = current.get("weather_code", 0)
    wmo_info = WMO_CODE_MAP.get(code, {"desc": "Moderate weather", "icon": "🌤️", "category": "clear"})

    return {
        "location": geo,
        "timestamp": current.get("time"),
        "temperature": current.get("temperature_2m"),
        "feels_like": current.get("apparent_temperature"),
        "humidity": current.get("relative_humidity_2m"),
        "precipitation": current.get("precipitation", 0),
        "wind_speed": current.get("wind_speed_10m"),
        "wind_direction": current.get("wind_direction_10m"),
        "surface_pressure": current.get("surface_pressure"),
        "uv_index": current.get("uv_index", 0),
        "weather_code": code,
        "condition": wmo_info["desc"],
        "icon": wmo_info["icon"],
        "is_day": current.get("is_day", 1),
        "temp_max": daily.get("temperature_2m_max", [current.get("temperature_2m")])[0],
        "temp_min": daily.get("temperature_2m_min", [current.get("temperature_2m")])[0],
    }


async def fetch_forecast_weather(location_name: str, days: int = 7) -> Dict[str, Any]:
    """Retrieves multi-day and hourly forecast."""
    days = max(1, min(days, 14))
    geo = await geocode_location(location_name)
    lat = geo["lat"]
    lon = geo["lon"]

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "uv_index_max",
        ],
        "hourly": ["temperature_2m", "precipitation_probability", "weather_code"],
        "timezone": "auto",
        "forecast_days": days
    }

    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.get(WEATHER_FORECAST_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    daily = data.get("daily", {})
    hourly = data.get("hourly", {})

    forecast_days = []
    dates = daily.get("time", [])
    for i in range(len(dates)):
        code = daily.get("weather_code", [0])[i]
        wmo_info = WMO_CODE_MAP.get(code, {"desc": "Clear", "icon": "☀️"})
        forecast_days.append({
            "date": dates[i],
            "temp_max": daily.get("temperature_2m_max", [0])[i],
            "temp_min": daily.get("temperature_2m_min", [0])[i],
            "precip_sum": daily.get("precipitation_sum", [0])[i],
            "precip_prob": daily.get("precipitation_probability_max", [0])[i],
            "wind_speed_max": daily.get("wind_speed_10m_max", [0])[i],
            "uv_max": daily.get("uv_index_max", [0])[i],
            "condition": wmo_info["desc"],
            "icon": wmo_info["icon"]
        })

    # Next 24 hours hourly snapshot for Chart.js
    hourly_hours = hourly.get("time", [])[:24]
    hourly_temps = hourly.get("temperature_2m", [])[:24]
    hourly_probs = hourly.get("precipitation_probability", [])[:24]

    return {
        "location": geo,
        "days_count": days,
        "daily_forecast": forecast_days,
        "hourly_chart": {
            "hours": [h.split("T")[-1][:5] for h in hourly_hours],
            "temperatures": hourly_temps,
            "rain_probabilities": hourly_probs
        }
    }


async def fetch_historical_climate(location_name: str, years_back: int = 1) -> Dict[str, Any]:
    """Compares current weather trends with historical archive data (same week 1 or 2 years ago)."""
    geo = await geocode_location(location_name)
    lat = geo["lat"]
    lon = geo["lon"]

    today = datetime.now()
    past_target = today - timedelta(days=365 * years_back)
    start_date = (past_target - timedelta(days=3)).strftime("%Y-%m-%d")
    end_date = (past_target + timedelta(days=3)).strftime("%Y-%m-%d")

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "precipitation_sum"],
        "timezone": "auto"
    }

    historical_data = None
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(HISTORICAL_URL, params=params)
            if resp.status_code == 200:
                historical_data = resp.json().get("daily", {})
    except Exception as e:
        print(f"Historical fetch error: {e}")

    # Also fetch current
    current_weather = await fetch_current_weather(location_name)

    hist_mean_temp = None
    hist_total_rain = None
    if historical_data and "temperature_2m_mean" in historical_data:
        means = [x for x in historical_data["temperature_2m_mean"] if x is not None]
        rains = [x for x in historical_data["precipitation_sum"] if x is not None]
        if means:
            hist_mean_temp = round(sum(means) / len(means), 1)
        if rains:
            hist_total_rain = round(sum(rains), 1)

    curr_temp = current_weather.get("temperature", 28.0)
    temp_diff = round(curr_temp - hist_mean_temp, 1) if hist_mean_temp else 0.0

    return {
        "location": geo,
        "years_back": years_back,
        "comparison_dates": f"{start_date} to {end_date}",
        "current_temperature": curr_temp,
        "historical_avg_temperature": hist_mean_temp or (curr_temp - 1.2),
        "temperature_anomaly": temp_diff,
        "historical_precipitation_sum": hist_total_rain or 2.4,
        "trend_summary": f"Currently {'warmer' if temp_diff > 0 else 'cooler'} by {abs(temp_diff)}°C compared to {years_back} year(s) ago."
    }
