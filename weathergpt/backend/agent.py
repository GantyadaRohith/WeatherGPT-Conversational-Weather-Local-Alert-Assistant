"""
agent.py
Adapter connecting the FastAPI backend to the LangChain / LangGraph StateGraph engine.
Preserves backwards compatibility with React frontend and compulsory trace inspection.
"""

import time
from typing import Any, Dict, List, Optional
from backend.langgraph_agent import weather_graph


class WeatherAgent:
    def __init__(self):
        self.last_location = "New Delhi"

    async def run(
        self,
        user_query: str,
        language: str = "en",
        session_history: Optional[List[Dict[str, str]]] = None,
        fixed_location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs user request through the compiled LangGraph StateGraph:
        SupervisorNode -> ToolExecutorNode -> AntiHallucinationGuardNode -> SynthesizerNode -> TraceGenerator
        """
        loc = fixed_location or self.last_location
        initial_state = {
            "user_query": user_query,
            "language": language or "en",
            "fixed_location": loc,
            "tool_name": None,
            "tool_params": {},
            "tool_data": None,
            "is_domain_relevant": True,
            "grounding_score": 0.0,
            "citation": "",
            "reply_text": "",
            "voice_summary": "",
            "trace": {},
            "t_start": time.time()
        }

        # Invoke LangGraph
        result_state = await weather_graph.ainvoke(initial_state)

        tool_data = result_state.get("tool_data") or {}
        tool_name = result_state.get("tool_name")

        # Unpack telemetry cards for React frontend components
        weather_card = None
        forecast_data = None
        advisory_data = None
        historical_data = None
        alerts_list = []

        if tool_name == "get_current_weather":
            weather_card = tool_data.get("current")
            alerts_list = tool_data.get("alerts", [])
        elif tool_name == "get_forecast":
            forecast_data = tool_data.get("forecast")
            weather_card = tool_data.get("current")
            alerts_list = tool_data.get("alerts", [])
        elif tool_name == "get_crop_advisory":
            advisory_data = tool_data.get("advisory")
            weather_card = tool_data.get("weather")
            alerts_list = tool_data.get("alerts", [])
        elif tool_name == "get_severe_alerts":
            alerts_list = tool_data.get("alerts", [])
            weather_card = tool_data.get("weather")
        elif tool_name == "get_historical_climate":
            historical_data = tool_data.get("historical")
            weather_card = tool_data.get("current")
        elif tool_name == "get_commute_advisory":
            advisory_data = tool_data.get("commute")
            weather_card = tool_data.get("weather")

        return {
            "reply": result_state.get("reply_text", ""),
            "voice_summary": result_state.get("voice_summary", ""),
            "trace": result_state.get("trace", {}),
            "weather_card": weather_card,
            "forecast_data": forecast_data,
            "advisory_data": advisory_data,
            "historical_data": historical_data,
            "alerts": alerts_list,
            "language": language
        }
