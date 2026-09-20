"""
translations.py
Multilingual dictionary and localization for Indian languages:
English (en), Hindi (hi), Bengali (bn), Tamil (ta), Telugu (te), Marathi (mr).
"""

from typing import Dict, Any

LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
    "bn": "বাংলা (Bengali)",
    "ta": "தமிழ் (Tamil)",
    "te": "తెలుగు (Telugu)",
    "mr": "मराठी (Marathi)"
}

TRANSLATION_MAP = {
    "hi": {
        "current_weather_in": "{city} में वर्तमान मौसम",
        "temperature": "तापमान",
        "feels_like": "महसूस हो रहा है",
        "humidity": "आर्द्रता (नमी)",
        "wind_speed": "हवा की गति",
        "precipitation": "बारिश",
        "forecast_days": "{city} के लिए {days} दिनों का मौसम पूर्वानुमान",
        "historical_climate": "{city} का ऐतिहासिक मौसम रुझान",
        "crop_advisory": "किसान कृषि सलाह",
        "commute_advisory": "यात्रा एवं दैनिक सलाह",
        "extreme_alert": "मौसम चेतावनी अलर्ट",
        "tool_used": "उपयोग किया गया टूल",
        "reason": "चयन का कारण",
        "parameters": "पैरामीटर्स",
        "spray_safe": "कीटनाशक छिड़काव: सुरक्षित",
        "spray_unsafe": "कीटनाशक छिड़काव: न करें",
        "irrigate": "सिंचाई की आवश्यकता है",
        "postpone_irrigation": "सिंचाई स्थगित करें",
        "clear": "साफ़ मौसम",
        "cloudy": "बादल छाए रहेंगे",
        "rain": "बारिश की संभावना",
        "storm": "तूफ़ान / आंधी",
        "hot": "अत्यधिक गर्मी"
    },
    "bn": {
        "current_weather_in": "{city}-তে বর্তমান আবহাওয়া",
        "temperature": "তাপমাত্রা",
        "feels_like": "অনুভূত তাপমাত্রা",
        "humidity": "আর্দ্রতা",
        "wind_speed": "বাতাসের গতি",
        "precipitation": "বৃষ্টিপাত",
        "forecast_days": "{city}-র আগামী {days} দিনের আবহাওয়ার পূর্বাভাস",
        "historical_climate": "{city}-র ঐতিহাসিক আবহাওয়া বিশ্লেষণ",
        "crop_advisory": "কৃষকদের জন্য পরামর্শ",
        "commute_advisory": "যাতায়াত ও দৈনিক সতর্কতা",
        "extreme_alert": "জরুরি আবহাওয়া সতর্কতা",
        "tool_used": "ব্যবহৃত টুল",
        "reason": "টুল নির্বাচনের কারণ",
        "parameters": "প্যারামিটার",
        "spray_safe": "কীটনাশক স্প্রে: নিরাপদ",
        "spray_unsafe": "কীটনাশক স্প্রে: করবেন না",
        "irrigate": "সেচ প্রয়োজন",
        "postpone_irrigation": "সেচ স্থগিত রাখুন",
        "clear": "পরিষ্কার আকাশ",
        "cloudy": "মেঘলা আকাশ",
        "rain": "বৃষ্টির সম্ভাবনা",
        "storm": "ঝড়বৃষ্টি",
        "hot": "তীব্র গরম"
    },
    "ta": {
        "current_weather_in": "{city} தற்போதைய வானிலை",
        "temperature": "வெப்பநிலை",
        "feels_like": "உணரப்படும் வெப்பம்",
        "humidity": "ஈரப்பதம்",
        "wind_speed": "காற்றின் வேகம்",
        "precipitation": "மழைப்பொழிவு",
        "forecast_days": "{city} அடுத்த {days} நாட்களுக்கான வானிலை முன்னறிவிப்பு",
        "historical_climate": "{city} வரலாற்று காலநிலை பகுப்பாய்வு",
        "crop_advisory": "விவசாய பயிர் ஆலோசனை",
        "commute_advisory": "பயண வழிகாட்டுதல்",
        "extreme_alert": "தீவிர வானிலை எச்சரிக்கை",
        "tool_used": "பயன்படுத்தப்பட்ட கருவி",
        "reason": "காரணம்",
        "parameters": "அளவீடுகள்",
        "spray_safe": "பூச்சிக்கொல்லி தெளிக்கலாம்",
        "spray_unsafe": "பூச்சிக்கொல்லி தெளிக்க வேண்டாம்",
        "irrigate": "பாசனம் தேவை",
        "postpone_irrigation": "பாசனத்தை ஒத்திவைக்கவும்",
        "clear": "தெளிவான வானம்",
        "cloudy": "மேகமூட்டம்",
        "rain": "மழை வாய்ப்பு",
        "storm": "இடியுடன் கூடிய புயல்",
        "hot": "கடுமையான வெப்பம்"
    },
    "te": {
        "current_weather_in": "{city} ప్రస్తుత వాతావరణం",
        "temperature": "ఉష్ణోగ్రత",
        "feels_like": "అనిపించే ఉష్ణోగ్రత",
        "humidity": "తేమ శాతం",
        "wind_speed": "గాలి వేగం",
        "precipitation": "వర్షపాతం",
        "forecast_days": "{city} కోసం {days} రోజుల వాతావరణ అంచనా",
        "historical_climate": "{city} చారిత్రక వాతావరణ విశ్లేషణ",
        "crop_advisory": "రైతుల పంట సలహా",
        "commute_advisory": "ప్రయాణ సలహా",
        "extreme_alert": "తీవ్ర వాతావరణ హెచ్చరిక",
        "tool_used": "ఎంచుకున్న టూల్",
        "reason": "ఎంపిక కారణం",
        "parameters": "పారామితులు",
        "spray_safe": "పురుగుమందు పిచికారీ: అనుకూలం",
        "spray_unsafe": "పురుగుమందు పిచికారీ: వద్దు",
        "irrigate": "నీటి పారుదల అవసరం",
        "postpone_irrigation": "నీటి పారుదల వాయిదా వేయండి",
        "clear": "నిర్మలమైన ఆకాశం",
        "cloudy": "మేఘావృతం",
        "rain": "వర్షం సూచన",
        "storm": "ఉరుములతో కూడిన తుఫాను",
        "hot": "తీవ్రమైన ఎండ"
    },
    "mr": {
        "current_weather_in": "{city} मधील चालू हवामान",
        "temperature": "तापमान",
        "feels_like": "जाणवणारे तापमान",
        "humidity": "हवेतील आर्द्रता",
        "wind_speed": "वाऱ्याचा वेग",
        "precipitation": "पाऊस",
        "forecast_days": "{city} चे पुढील {days} दिवसांचे हवामान अंदाज",
        "historical_climate": "{city} चा ऐतिहासिक हवामान कल",
        "crop_advisory": "शेतकरी पीक सल्ला",
        "commute_advisory": "प्रवास व सुरक्षा सल्ला",
        "extreme_alert": "हवामान इशारा अलर्ट",
        "tool_used": "वापरलेले टूल",
        "reason": "टूल निवडण्याचे कारण",
        "parameters": "पॅरामीटर्स",
        "spray_safe": "कीटकनाशक फवारणी: योग्य वेळ",
        "spray_unsafe": "कीटकनाशक फवारणी: करू नका",
        "irrigate": "पाणी देण्याची गरज आहे",
        "postpone_irrigation": "पाणी देणे पुढे ढकला",
        "clear": "निरभ्र आकाश",
        "cloudy": "ढगाळ वातावरण",
        "rain": "पावसाची शक्यता",
        "storm": "वादळी वारे / पाऊस",
        "hot": "उष्णतेची लाट"
    }
}


def get_translation(key: str, lang: str = "en", **kwargs) -> str:
    """Returns localized string, falling back to English."""
    if lang not in TRANSLATION_MAP or key not in TRANSLATION_MAP[lang]:
        # English fallback
        en_defaults = {
            "current_weather_in": "Current Weather in {city}",
            "temperature": "Temperature",
            "feels_like": "Feels Like",
            "humidity": "Humidity",
            "wind_speed": "Wind Speed",
            "precipitation": "Precipitation",
            "forecast_days": "{days}-Day Weather Forecast for {city}",
            "historical_climate": "Historical Climate Analysis for {city}",
            "crop_advisory": "Farmer Agricultural Advisory",
            "commute_advisory": "Commuter & Safety Advisory",
            "extreme_alert": "Extreme Weather Alert",
            "tool_used": "Tool Selected",
            "reason": "Reason",
            "parameters": "Parameters",
            "spray_safe": "Pesticide Spray: Safe & Favorable",
            "spray_unsafe": "Pesticide Spray: Restricted / Unfavorable",
            "irrigate": "Irrigation Recommended",
            "postpone_irrigation": "Postpone Irrigation",
            "clear": "Clear Skies",
            "cloudy": "Cloudy",
            "rain": "Rain Expected",
            "storm": "Thunderstorm",
            "hot": "High Heat"
        }
        raw = en_defaults.get(key, key)
    else:
        raw = TRANSLATION_MAP[lang][key]

    return raw.format(**kwargs) if kwargs else raw
