"""
advisories.py
Generates contextual agricultural crop advisories for Indian farmers,
computes dynamic Best Crop suitability rankings based on live telemetry,
and provides commuter/travel advisories based on meteorological metrics.
"""

from typing import Any, Dict, List, Optional, Tuple

CROP_PROFILES = {
    # Cereals & Grains
    "wheat": {
        "name": "Wheat (गेहूं / Wheat)",
        "category": "Cereal",
        "ideal_temp": (15, 25),
        "water_need": "medium",
        "rain_sensitive_stages": ["flowering", "grain filling", "harvesting"],
        "advice_dry": "Maintain light irrigation during crown root initiation and flowering. Avoid heavy watering.",
        "advice_wet": "High humidity may trigger rust/powdery mildew. Delay pesticide spray until foliage dries."
    },
    "rice": {
        "name": "Paddy / Rice (धान / Rice)",
        "category": "Cereal",
        "ideal_temp": (22, 35),
        "water_need": "high",
        "rain_sensitive_stages": ["tillering", "panicle initiation"],
        "advice_dry": "Ensure 3-5 cm standing water during panicle stage. Prioritize canal/pump irrigation.",
        "advice_wet": "Rain is favorable for paddy. Open field drainage channels to prevent excessive submergence."
    },
    "paddy": {
        "name": "Paddy / Rice (धान / Paddy)",
        "category": "Cereal",
        "ideal_temp": (22, 35),
        "water_need": "high",
        "rain_sensitive_stages": ["tillering", "panicle initiation"],
        "advice_dry": "Ensure 3-5 cm standing water during panicle stage. Prioritize canal/pump irrigation.",
        "advice_wet": "Rain is favorable for paddy. Open field drainage channels to prevent excessive submergence."
    },
    "maize": {
        "name": "Maize / Corn (मक्का / Maize)",
        "category": "Cereal",
        "ideal_temp": (20, 32),
        "water_need": "medium",
        "rain_sensitive_stages": ["tasseling", "silking"],
        "advice_dry": "Critical moisture stage at tasseling and silking. Provide irrigation if dry spell exceeds 7 days.",
        "advice_wet": "Ensure prompt drainage; maize cannot tolerate waterlogging in early vegetative stages."
    },
    "corn": {
        "name": "Maize / Corn (मक्का / Corn)",
        "category": "Cereal",
        "ideal_temp": (20, 32),
        "water_need": "medium",
        "rain_sensitive_stages": ["tasseling", "silking"],
        "advice_dry": "Provide irrigation during knee-high and silking stages. Avoid moisture stress.",
        "advice_wet": "Ensure good drainage to protect root respiration."
    },
    "barley": {
        "name": "Barley (जौ / Barley)",
        "category": "Cereal",
        "ideal_temp": (14, 24),
        "water_need": "low",
        "rain_sensitive_stages": ["grain filling"],
        "advice_dry": "Barley is moderately drought tolerant. Provide 2-3 light irrigations at tillering and boot stages.",
        "advice_wet": "Avoid stagnant water; high moisture causes root rot and foliar blight."
    },

    # Millets / Nutri-Cereals (Drought Tolerant)
    "bajra": {
        "name": "Bajra / Pearl Millet (बाजरा / Bajra)",
        "category": "Millet",
        "ideal_temp": (25, 36),
        "water_need": "low",
        "rain_sensitive_stages": ["flowering"],
        "advice_dry": "Highly drought-hardy. Excellent crop for semi-arid zones. Requires minimal irrigation.",
        "advice_wet": "Excess rainfall during flowering can cause ergot. Ensure sandy soil drainage."
    },
    "jowar": {
        "name": "Jowar / Sorghum (ज्वार / Jowar)",
        "category": "Millet",
        "ideal_temp": (24, 34),
        "water_need": "low",
        "rain_sensitive_stages": ["grain formation"],
        "advice_dry": "Deep rooted and efficient water user. Irrigate only if prolonged dry spell during boot stage.",
        "advice_wet": "Wet weather during maturity may lead to grain mold; harvest promptly."
    },
    "ragi": {
        "name": "Ragi / Finger Millet (रागी / Ragi)",
        "category": "Millet",
        "ideal_temp": (20, 32),
        "water_need": "low",
        "rain_sensitive_stages": ["tillering"],
        "advice_dry": "Can withstand dry spells. Irrigate during transplanting and tillering if soil is dry.",
        "advice_wet": "Tolerates reasonable rain. Ensure weed control in wet initial growth."
    },

    # Commercial & Cash Crops
    "cotton": {
        "name": "Cotton (कपास / Cotton)",
        "category": "Cash Crop",
        "ideal_temp": (21, 35),
        "water_need": "medium",
        "rain_sensitive_stages": ["boll opening", "picking"],
        "advice_dry": "Scout for sucking pests (whitefly/thrips) in dry warm weather. Maintain optimum soil moisture.",
        "advice_wet": "Continuous rain during boll opening can damage fiber quality. Halt picking until dry sunny spells."
    },
    "sugarcane": {
        "name": "Sugarcane (गन्ना / Sugarcane)",
        "category": "Cash Crop",
        "ideal_temp": (24, 38),
        "water_need": "high",
        "rain_sensitive_stages": ["formative phase"],
        "advice_dry": "High water requirement. Schedule trash mulching to conserve moisture in peak summer.",
        "advice_wet": "Rain boosts cane elongation. Tie canes together (propping) to prevent lodging in high winds."
    },
    "tobacco": {
        "name": "Tobacco (तंबाकू / Tobacco)",
        "category": "Cash Crop",
        "ideal_temp": (20, 32),
        "water_need": "medium",
        "rain_sensitive_stages": ["curing", "harvesting"],
        "advice_dry": "Control moisture to maintain leaf texture and nicotine content.",
        "advice_wet": "Excess moisture damages leaf aroma and triggers damping-off. Avoid picking wet leaves."
    },

    # Oilseeds
    "mustard": {
        "name": "Mustard / Rapeseed (सरसों / Mustard)",
        "category": "Oilseed",
        "ideal_temp": (15, 25),
        "water_need": "low",
        "rain_sensitive_stages": ["pod development"],
        "advice_dry": "Irrigate at pod filling stage. Watch for aphid infestation if overcast conditions persist.",
        "advice_wet": "Cloudy and wet conditions increase aphid spread. Spray recommended bio-pesticide when clear."
    },
    "soybean": {
        "name": "Soybean (सोयाबीन / Soybean)",
        "category": "Oilseed",
        "ideal_temp": (22, 33),
        "water_need": "medium",
        "rain_sensitive_stages": ["pod initiation", "grain filling"],
        "advice_dry": "Critical irrigation needed at pod filling if dry spell exceeds 10 days.",
        "advice_wet": "Broad bed furrow (BBF) planting helps drain excess monsoon water and avoid root rot."
    },
    "groundnut": {
        "name": "Groundnut / Peanut (मूंगफली / Groundnut)",
        "category": "Oilseed",
        "ideal_temp": (22, 34),
        "water_need": "low",
        "rain_sensitive_stages": ["pegging", "pod development"],
        "advice_dry": "Adequate soil moisture is crucial during peg penetration into soil. Apply light irrigation.",
        "advice_wet": "Prolonged wet soil at maturity causes pod sprouting and aflatoxin development."
    },
    "sunflower": {
        "name": "Sunflower (सूरजमुखी / Sunflower)",
        "category": "Oilseed",
        "ideal_temp": (20, 32),
        "water_need": "medium",
        "rain_sensitive_stages": ["flowering", "seed filling"],
        "advice_dry": "Provide irrigation during bud initiation and seed development for high oil percentage.",
        "advice_wet": "High humidity and continuous rain during flowering cause head rot (Rhizopus)."
    },

    # Pulses & Legumes
    "chickpea": {
        "name": "Chickpea / Bengal Gram (चना / Chickpea)",
        "category": "Pulse",
        "ideal_temp": (16, 26),
        "water_need": "low",
        "rain_sensitive_stages": ["flowering", "podding"],
        "advice_dry": "Requires minimal water. One pre-flowering irrigation and one pod-formation irrigation suffice.",
        "advice_wet": "Cloudy wet weather triggers Ascochyta blight and pod borer attacks. Maintain field drainage."
    },
    "chana": {
        "name": "Gram / Chana (चना / Gram)",
        "category": "Pulse",
        "ideal_temp": (16, 26),
        "water_need": "low",
        "rain_sensitive_stages": ["flowering", "podding"],
        "advice_dry": "Deep rooted. Provide light irrigation only during pod development.",
        "advice_wet": "Avoid water accumulation; gram is highly sensitive to root wilt under excess wetness."
    },
    "tur": {
        "name": "Pigeon Pea / Arhar / Tur (अरहर/तूर / Tur)",
        "category": "Pulse",
        "ideal_temp": (22, 35),
        "water_need": "medium",
        "rain_sensitive_stages": ["podding"],
        "advice_dry": "Deep taproot system tolerates dry periods well. Irrigate at pod initiation.",
        "advice_wet": "Water stagnation causes Phytophthora blight. Ensure furrow drainage."
    },
    "arhar": {
        "name": "Pigeon Pea / Arhar (अरहर / Arhar)",
        "category": "Pulse",
        "ideal_temp": (22, 35),
        "water_need": "medium",
        "rain_sensitive_stages": ["podding"],
        "advice_dry": "Tolerates moisture stress. Maintain optimum moisture at flowering.",
        "advice_wet": "Clear excess rainwater immediately."
    },
    "moong": {
        "name": "Moong / Green Gram (मूंग / Moong)",
        "category": "Pulse",
        "ideal_temp": (25, 35),
        "water_need": "low",
        "rain_sensitive_stages": ["pod development"],
        "advice_dry": "Short duration (60-65 days). Requires only 2 irrigations if dry.",
        "advice_wet": "Rain during pod maturity can cause grain discoloration and pre-harvest sprouting."
    },
    "urad": {
        "name": "Urad / Black Gram (उड़द / Urad)",
        "category": "Pulse",
        "ideal_temp": (24, 34),
        "water_need": "low",
        "rain_sensitive_stages": ["pod filling"],
        "advice_dry": "Suitable for intercropping. Irrigate at pod development if rainfall is deficient.",
        "advice_wet": "Ensure field is well-drained to avoid yellow mosaic virus proliferation."
    },

    # Vegetables & Horticulture
    "tomato": {
        "name": "Tomato (टमाटर / Tomato)",
        "category": "Vegetable",
        "ideal_temp": (18, 30),
        "water_need": "medium",
        "rain_sensitive_stages": ["fruit setting"],
        "advice_dry": "Regular drip irrigation prevents blossom end rot. Mulch with straw.",
        "advice_wet": "Stake plants upright. Spray copper fungicide after rains to stop early/late blight."
    },
    "potato": {
        "name": "Potato (आलू / Potato)",
        "category": "Vegetable",
        "ideal_temp": (15, 24),
        "water_need": "medium",
        "rain_sensitive_stages": ["tuberization"],
        "advice_dry": "Provide light, frequent irrigations at tuber initiation stage. Earthing up is essential.",
        "advice_wet": "Cool, humid and cloudy weather strongly favors Late Blight. Give prophylactic Mancozeb spray."
    },
    "onion": {
        "name": "Onion (प्याज / Onion)",
        "category": "Vegetable",
        "ideal_temp": (15, 28),
        "water_need": "medium",
        "rain_sensitive_stages": ["bulb enlargement"],
        "advice_dry": "Maintain shallow moisture. Stop irrigation 15 days before harvest to improve shelf life.",
        "advice_wet": "High humidity invites purple blotch. Spray companion bio-fungicide once foliage dries."
    },
    "chilli": {
        "name": "Chilli / Mirchi (मिर्च / Chilli)",
        "category": "Spices & Veg",
        "ideal_temp": (20, 32),
        "water_need": "medium",
        "rain_sensitive_stages": ["flowering", "fruit set"],
        "advice_dry": "Irrigate regularly to prevent flower drop. Scout for thrips and mites in warm dry weather.",
        "advice_wet": "Waterlogging causes die-back and fruit rot (Anthracnose). Ensure raised bed drainage."
    },
    "vegetables": {
        "name": "Vegetables & Horticulture (सब्जियां / Vegetables)",
        "category": "Horticulture",
        "ideal_temp": (18, 30),
        "water_need": "medium",
        "rain_sensitive_stages": ["all"],
        "advice_dry": "Mulch beds to conserve soil moisture. Drip irrigate in early mornings or evenings.",
        "advice_wet": "Provide staking/support to tomato and climber vines. Clear excess drainage to prevent root rot."
    },

    # Fruits & Plantations
    "mango": {
        "name": "Mango (आम / Mango)",
        "category": "Fruit",
        "ideal_temp": (24, 38),
        "water_need": "medium",
        "rain_sensitive_stages": ["flowering", "fruit set"],
        "advice_dry": "Withhold irrigation 2 months prior to flowering. Resume watering after fruit set.",
        "advice_wet": "Rain during flowering washes away pollen and causes anthracnose. Avoid spraying during bloom."
    },
    "banana": {
        "name": "Banana (केला / Banana)",
        "category": "Fruit",
        "ideal_temp": (22, 35),
        "water_need": "high",
        "rain_sensitive_stages": ["bunch emergence"],
        "advice_dry": "Heavy water feeder. Irrigate every 3-4 days in summer. Maintain thick organic mulch.",
        "advice_wet": "Provide strong bamboo prop support against squally winds and torrential monsoon rains."
    },
    "citrus": {
        "name": "Citrus / Lemon / Orange (नींबू/संतरा / Citrus)",
        "category": "Fruit",
        "ideal_temp": (18, 32),
        "water_need": "medium",
        "rain_sensitive_stages": ["fruit development"],
        "advice_dry": "Avoid moisture stress during marble-sized fruit stage to avoid premature drop.",
        "advice_wet": "Water stagnation triggers gummosis and root decay. Form ring basin around tree trunks."
    },
    "tea": {
        "name": "Tea (चाय / Tea)",
        "category": "Plantation",
        "ideal_temp": (18, 30),
        "water_need": "high",
        "rain_sensitive_stages": ["flushing"],
        "advice_dry": "Maintain shade trees and overhead sprinkler irrigation during dry spring months.",
        "advice_wet": "Well-distributed rainfall is ideal. Ensure hillside contours prevent soil erosion."
    },
    "turmeric": {
        "name": "Turmeric (हल्दी / Turmeric)",
        "category": "Spices",
        "ideal_temp": (22, 35),
        "water_need": "medium",
        "rain_sensitive_stages": ["rhizome development"],
        "advice_dry": "Keep soil friable with straw mulch. Irrigate at 7-10 day intervals during rhizome growth.",
        "advice_wet": "Ensure raised ridges to prevent rhizome rot during peak monsoon spells."
    }
}


def rank_best_crops_for_weather(
    weather: Dict[str, Any],
    forecast: Dict[str, Any],
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Computes a dynamic Suitability Index (0-99%) for all 30+ crops
    based on current temperature, forecasted rain, wind, and humidity.
    Returns ranked list of the BEST crops suited to the active area right now.
    """
    temp = weather.get("temperature", 28.0)
    humidity = weather.get("humidity", 60)
    wind = weather.get("wind_speed", 10.0)
    rain_current = weather.get("precipitation", 0.0)

    daily = forecast.get("daily_forecast", [])[:3]
    max_rain_prob = max([d.get("precip_prob", 0) for d in daily]) if daily else 0
    total_rain_expected = sum([d.get("precip_sum", 0) for d in daily]) if daily else 0

    scores = []
    seen_names = set()

    for key, p in CROP_PROFILES.items():
        base_name = p["name"].split(" (")[0]
        if base_name in seen_names:
            continue
        seen_names.add(base_name)

        min_t, max_t = p["ideal_temp"]
        water_req = p.get("water_need", "medium")

        # 1. Temperature Fitness (Base 70 pts)
        if min_t <= temp <= max_t:
            temp_score = 70.0
        elif temp < min_t:
            diff = min_t - temp
            temp_score = max(20.0, 70.0 - (diff * 5.0))
        else:
            diff = temp - max_t
            temp_score = max(20.0, 70.0 - (diff * 5.0))

        # 2. Moisture / Rain Fitness (Base 30 pts)
        rain_score = 25.0
        if water_req == "high":
            if total_rain_expected > 15.0 or humidity > 70:
                rain_score = 30.0
            elif total_rain_expected < 2.0 and humidity < 40:
                rain_score = 15.0
        elif water_req == "low":  # Millets, gram, mustard
            if total_rain_expected < 5.0:
                rain_score = 30.0
            elif total_rain_expected > 25.0 or max_rain_prob > 75:
                rain_score = 10.0
        else:  # Medium
            if total_rain_expected < 20.0:
                rain_score = 26.0
            else:
                rain_score = 18.0

        total_score = min(98.0, round(temp_score + rain_score, 1))

        if total_score >= 88:
            rating = "Highly Recommended"
            badge = "Ideal"
        elif total_score >= 76:
            rating = "Well Suited"
            badge = "Good"
        elif total_score >= 60:
            rating = "Moderately Feasible"
            badge = "Moderate"
        else:
            rating = "Low Suitability"
            badge = "Challenging"

        rationale = (
            f"Ideal temp range is {min_t}-{max_t}°C (current {temp}°C). "
            f"Moisture demand is {water_req} ({'favorable rain' if total_rain_expected > 5 else 'calm dry conditions'})."
        )

        scores.append({
            "crop_key": key,
            "crop_name": p["name"],
            "category": p.get("category", "General"),
            "score": total_score,
            "rating": rating,
            "badge": badge,
            "ideal_temp": f"{min_t}-{max_t}°C",
            "water_need": water_req.capitalize(),
            "rationale": rationale,
            "tip": p["advice_wet"] if total_rain_expected > 5.0 else p["advice_dry"]
        })

    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:top_n]


def generate_crop_advisory(
    weather: Dict[str, Any],
    forecast: Dict[str, Any],
    crop_name: str = "general"
) -> Dict[str, Any]:
    """Generates an actionable agricultural advisory with Best Crop ranking."""
    temp = weather.get("temperature", 28.0)
    humidity = weather.get("humidity", 60)
    wind = weather.get("wind_speed", 10.0)
    rain_current = weather.get("precipitation", 0.0)
    loc_name = weather.get("location", {}).get("name", "Current Area")

    # Check rain in upcoming 3 days
    daily = forecast.get("daily_forecast", [])[:3]
    rain_upcoming_max = max([d.get("precip_prob", 0) for d in daily]) if daily else 0
    total_rain_expected = sum([d.get("precip_sum", 0) for d in daily]) if daily else 0

    crop_clean = crop_name.lower().strip()
    is_best_query = any(w in crop_clean for w in ["best", "recommend", "ranking", "all", "which", "suggest", "suitable"])

    # Compute top crop rankings for the active weather
    top_crops = rank_best_crops_for_weather(weather, forecast, top_n=5)

    profile = None
    for k, v in CROP_PROFILES.items():
        if k in crop_clean or crop_clean in k:
            profile = v
            break

    if not profile:
        if is_best_query and top_crops:
            # Use top ranked crop as primary
            profile = CROP_PROFILES.get(top_crops[0]["crop_key"], CROP_PROFILES["rice"])
        else:
            # Dynamic agronomic heuristic for any unlisted crop
            profile = {
                "name": crop_name.title() if crop_name not in ["general", ""] else "General Agricultural Crops",
                "ideal_temp": (18, 32),
                "advice_dry": "Maintain optimal root zone moisture through timely morning irrigation.",
                "advice_wet": "Clear field furrows to prevent root saturation and fungal spore germination."
            }

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
    crop_specific_tip = profile.get("advice_wet") if total_rain_expected > 5.0 else profile.get("advice_dry")

    return {
        "crop": profile["name"],
        "is_best_recommendation": is_best_query,
        "ranked_crops": top_crops,
        "irrigation_action": irrigation_badge,
        "irrigation_details": irrigation_rec,
        "spray_feasible": spray_allowed,
        "spray_guidance": "SAFE TO SPRAY: Winds are calm (<18 km/h) and no rainfall is predicted." if spray_allowed else "DO NOT SPRAY: " + " ".join(spray_reasons),
        "crop_tip": crop_specific_tip,
        "summary": f"Advisory for {profile['name']} at {loc_name}: {irrigation_badge} irrigation status. Spraying is {'PERMITTED' if spray_allowed else 'RESTRICTED'}."
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

