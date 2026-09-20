"""
llm_client.py
Multi-provider LLM & Multi-Agent orchestration engine for WeatherGPT.
Loads configuration from .env using python-dotenv.
"""

import os
import json
import time
from typing import Any, Dict, List, Optional, Tuple
import httpx
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

# In-memory runtime configuration for LLM provider and keys
LLM_CONFIG = {
    "provider": os.environ.get("WEATHER_LLM_PROVIDER", "local"),  # "local", "groq", "gemini", "openai"
    "groq_api_key": os.environ.get("GROQ_API_KEY", ""),
    "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
    "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
    "groq_model": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
    "gemini_model": os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"),
    "openai_model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
}


SYSTEM_PROMPT = """You are WeatherGPT, an expert agentic meteorological and local alert assistant for India.
You have access to live tools:
1. get_current_weather(location): Real-time observations (temp, feels like, humidity, wind, UV, precipitation).
2. get_forecast(location, days): Multi-day forecast (1-14 days) and 24-hr hourly trend.
3. get_crop_advisory(location, crop): Agricultural advice for Indian farmers (wheat, paddy, cotton, mustard, etc.) regarding pesticide spraying feasibility, irrigation scheduling, and crop protection.
4. get_severe_alerts(location): Extreme weather hazard threshold check (cyclones, cloudbursts, heatwaves, frost).
5. get_historical_climate(location, years_back): Climate anomaly analysis comparing current weather to historical archive data from the same week in past years.
6. get_commute_advisory(location): Commute and outdoor safety guidance.

CRITICAL ACCURACY & NO-HALLUCINATION RULES:
- Only answer queries related to weather, forecasting, agriculture/crops, climate trends, or disaster alerts.
- Every single fact, temperature number, and forecast detail MUST strictly come from the provided ground-truth tool data.
- NEVER invent weather metrics, dates, or cyclone warnings not in the retrieved data.
- If an Indian language is requested (Hindi, Bengali, Tamil, Telugu, Marathi), respond fluently in that language."""


class LLMClient:
    def __init__(self):
        self.config = LLM_CONFIG

    def update_config(self, provider: str, api_key: Optional[str] = None, model: Optional[str] = None):
        """Updates runtime LLM settings."""
        self.config["provider"] = provider
        if provider == "groq" and api_key:
            self.config["groq_api_key"] = api_key
            if model:
                self.config["groq_model"] = model
        elif provider == "gemini" and api_key:
            self.config["gemini_api_key"] = api_key
            if model:
                self.config["gemini_model"] = model
        elif provider == "openai" and api_key:
            self.config["openai_api_key"] = api_key
            if model:
                self.config["openai_model"] = model

    async def call_groq(self, prompt: str, system: str = SYSTEM_PROMPT) -> Tuple[Optional[str], Optional[str]]:
        """Calls Groq API with automatic model fallback."""
        key = self.config.get("groq_api_key")
        if not key:
            return None, None
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        
        # Ordered list of models to try
        preferred_model = self.config.get("groq_model") or "openai/gpt-oss-20b"
        models_to_try = [preferred_model, "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "llama-3.3-70b-versatile"]
        seen = set()
        unique_models = [m for m in models_to_try if not (m in seen or seen.add(m))]

        async with httpx.AsyncClient(timeout=15.0) as client:
            for model_name in unique_models:
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 800
                }
                try:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["choices"][0]["message"]["content"]
                        return text, f"groq:{model_name}"
                    else:
                        print(f"Groq model {model_name} returned {resp.status_code}: {resp.text[:100]}")
                except Exception as e:
                    print(f"Groq request error for {model_name}: {e}")

        return None, None

    async def call_gemini(self, prompt: str, system: str = SYSTEM_PROMPT) -> Optional[str]:
        """Calls Google Gemini API."""
        key = self.config.get("gemini_api_key")
        if not key:
            return None
        model = self.config.get("gemini_model", "gemini-1.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{system}\n\nUser Request: {prompt}"}]}
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 800
            }
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    return candidates[0]["content"]["parts"][0]["text"]
        return None

    async def call_openai(self, prompt: str, system: str = SYSTEM_PROMPT) -> Optional[str]:
        """Calls OpenAI API."""
        key = self.config.get("openai_api_key")
        if not key:
            return None
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "model": self.config.get("openai_model", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 800
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        return None

    async def synthesize_response(
        self,
        user_query: str,
        tool_name: str,
        tool_data: Dict[str, Any],
        language: str = "en"
    ) -> Tuple[Optional[str], str]:
        """
        Synthesizes natural language response using active LLM provider.
        Returns: (synthesized_text, provider_used)
        """
        provider = self.config["provider"]
        if provider == "local":
            return None, "langgraph_local_agent"

        prompt = f"""
User Query: "{user_query}"
Language: {language}
Selected Tool: {tool_name}
Ground Truth Retrieved Data: {json.dumps(tool_data, default=str)}

Task: Provide a natural, empathetic, and comprehensive response answering the user's weather/advisory query.
- STRICT GROUNDING: Use ONLY the ground truth retrieved data above.
- Answer in the requested language ({language}).
- For farmers, explain irrigation and pesticide spraying safety clearly based on the provided numbers.
- For extreme hazards, clearly state precautions and actions required.
"""
        try:
            if provider == "groq" and self.config.get("groq_api_key"):
                res_text, model_used = await self.call_groq(prompt)
                if res_text:
                    return res_text, model_used or f"groq:{self.config.get('groq_model')}"
            elif provider == "gemini" and self.config.get("gemini_api_key"):
                res = await self.call_gemini(prompt)
                if res:
                    return res, f"gemini:{self.config.get('gemini_model')}"
            elif provider == "openai" and self.config.get("openai_api_key"):
                res = await self.call_openai(prompt)
                if res:
                    return res, f"openai:{self.config.get('openai_model')}"
        except Exception as e:
            print(f"LLM synthesis fallback: {e}")

        return None, "langgraph_local_agent"


# Global singleton instance
llm_client = LLMClient()
