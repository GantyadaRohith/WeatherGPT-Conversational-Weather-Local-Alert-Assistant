import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import FixedWeatherHero from './components/FixedWeatherHero';
import WeatherTelemetryGrid from './components/WeatherTelemetryGrid';
import HourlyChart from './components/HourlyChart';
import AgroAdvisoryCard from './components/AgroAdvisoryCard';
import ToolTraceCard from './components/ToolTraceCard';
import Sidebar from './components/Sidebar';
import SettingsModal from './components/SettingsModal';
import HazardAlertBanner from './components/HazardAlertBanner';

export default function App() {
  // App State
  const [language, setLanguage] = useState('en');
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [llmProvider, setLlmProvider] = useState('local');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Fixed Location Hero State (Apple Weather Style)
  const [fixedCity, setFixedCity] = useState('New Delhi');
  const [heroData, setHeroData] = useState(null);
  const [heroLoading, setHeroLoading] = useState(false);

  // Chat & Agent State
  const [messages, setMessages] = useState([
    {
      id: 'init',
      sender: 'assistant',
      text: 'Namaste! I am **WeatherGPT**, an AI-powered conversational weather & local alert assistant. Ask me in **English, हिन्दी, বাংলা, தமிழ், తెలుగు, or मराठी** for real-time weather, 14-day forecasts, Indian farmer crop advisories, or disaster alerts.',
      trace: {
        tool_picked: 'system_init',
        parameters: { fixed_location: 'New Delhi', mode: 'multi_agent' },
        reason: 'Initialized multi-agent orchestration pipelines and live Open-Meteo telemetry.',
        confidence: 1.0,
        latency_ms: 0,
        llm_engine: 'local_agent',
        agent_orchestration: ['Supervisor_Router', 'Tool_Dispatch', 'Domain_Specialist', 'Synthesizer']
      }
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  // Watchdog & Alerts State
  const [savedLocations, setSavedLocations] = useState([]);
  const [activeHazard, setActiveHazard] = useState(null);

  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Load Fixed Weather Hero Data
  const fetchHeroData = async (city) => {
    setHeroLoading(true);
    try {
      const res = await fetch(`/api/weather/hero?city=${encodeURIComponent(city)}`);
      if (res.ok) {
        const data = await res.json();
        setHeroData(data);
        if (data.alerts && data.alerts.length > 0) {
          setActiveHazard(data.alerts[0]);
        } else {
          // Clear active hazard when active location is safe
          setActiveHazard(null);
        }
      }
    } catch (e) {
      console.warn('Hero weather fetch error:', e);
    } finally {
      setHeroLoading(false);
    }
  };

  // Load Saved Locations
  const fetchSavedLocations = async () => {
    try {
      const res = await fetch('/api/saved-locations');
      if (res.ok) {
        const data = await res.json();
        setSavedLocations(data);
      }
    } catch (e) {
      console.warn('Saved locations fetch error:', e);
    }
  };

  // Run Watchdog Hazard Check (strictly for saved list status, never hijacks current location's banner)
  const checkWatchdog = async () => {
    try {
      const res = await fetch('/api/alerts/watchdog-check');
      if (res.ok) {
        const results = await res.json();
        // Only trigger banner if the alert is directly for the user's fixed/active location
        const activeAlert = results.find(
          r => r.location?.toLowerCase() === fixedCity?.toLowerCase() && r.active_alerts && r.active_alerts.length > 0
        );
        if (activeAlert) {
          setActiveHazard(activeAlert.active_alerts[0]);
        }
      }
    } catch (e) {
      console.warn('Watchdog check error:', e);
    }
  };

  // Check LLM Config
  const fetchLLMConfig = async () => {
    try {
      const res = await fetch('/api/config/llm');
      if (res.ok) {
        const data = await res.json();
        setLlmProvider(data.provider || 'local');
      }
    } catch (e) {
      console.warn('LLM config fetch error:', e);
    }
  };

  useEffect(() => {
    fetchHeroData(fixedCity);
    fetchSavedLocations();
    fetchLLMConfig();
    checkWatchdog();

    const timer = setInterval(checkWatchdog, 60000);
    return () => clearInterval(timer);
  }, []);

  // Scroll Chat to Bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Handle Speech-to-Text (STT)
  const toggleSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech Recognition is not supported in this browser. Please type your query.');
      return;
    }

    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    recognition.continuous = false;
    recognition.interimResults = false;

    const langCodeMap = {
      en: 'en-IN',
      hi: 'hi-IN',
      bn: 'bn-IN',
      ta: 'ta-IN',
      te: 'te-IN',
      mr: 'mr-IN'
    };
    recognition.lang = langCodeMap[language] || 'en-IN';

    recognition.onstart = () => setIsRecording(true);
    recognition.onresult = (e) => {
      const text = e.results[0][0].transcript;
      setInputText(text);
      setIsRecording(false);
      handleSendMessage(text);
    };
    recognition.onerror = () => setIsRecording(false);
    recognition.onend = () => setIsRecording(false);

    recognition.start();
  };

  // Handle Text-to-Speech (TTS)
  const speakText = (text, lang = 'en') => {
    if (!('speechSynthesis' in window) || !voiceEnabled) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const langCodeMap = {
      en: 'en-IN',
      hi: 'hi-IN',
      bn: 'bn-IN',
      ta: 'ta-IN',
      te: 'te-IN',
      mr: 'mr-IN'
    };
    utterance.lang = langCodeMap[lang] || 'en-IN';
    utterance.rate = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  // Send Chat Message
  const handleSendMessage = async (customText = null, customLang = null) => {
    const query = (customText !== null ? customText : inputText).trim();
    if (!query) return;

    const activeLang = customLang || language;
    const userMsg = { id: 'u_' + Date.now(), sender: 'user', text: query };
    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsTyping(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          language: activeLang,
          fixed_location: fixedCity
        })
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      const assistantMsg = {
        id: 'a_' + Date.now(),
        sender: 'assistant',
        text: data.reply,
        trace: data.trace,
        weather_card: data.weather_card,
        forecast_data: data.forecast_data,
        advisory_data: data.advisory_data,
        historical_data: data.historical_data,
        past_data: data.past_data,
        alerts: data.alerts,
        voice_summary: data.voice_summary,
        language: data.language
      };

      setMessages((prev) => [...prev, assistantMsg]);

      // Voice readout if enabled
      if (voiceEnabled && data.voice_summary) {
        speakText(data.voice_summary, data.language || activeLang);
      }

      // Voice readout if enabled
      if (voiceEnabled && data.voice_summary) {
        speakText(data.voice_summary, data.language || activeLang);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: 'err_' + Date.now(),
          sender: 'assistant',
          text: `⚠️ Error communicating with WeatherGPT agent (${err.message}). Ensure the backend server is running.`,
          trace: {
            tool_picked: 'error_fallback',
            parameters: { error: err.message },
            reason: 'Network or server exception during agent invocation.',
            latency_ms: 30,
            llm_engine: 'fallback'
          }
        }
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  // Change Fixed Location
  const handleCityChange = (city) => {
    setFixedCity(city);
    fetchHeroData(city);
  };

  // Real GPS Geolocation Handler with reverse geocoding
  const handleGPSClick = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }
    setHeroLoading(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const lat = pos.coords.latitude;
          const lon = pos.coords.longitude;
          const res = await fetch(`/api/weather/reverse-geocode?lat=${lat}&lon=${lon}`);
          if (res.ok) {
            const data = await res.json();
            const cityName = data.name || 'Current Location';
            setFixedCity(cityName);
            fetchHeroData(cityName);
          } else {
            handleCityChange('New Delhi');
          }
        } catch (err) {
          console.warn('Reverse geocode error:', err);
          handleCityChange('New Delhi');
        }
      },
      (err) => {
        console.warn('Geolocation permission error:', err);
        alert('Location access was denied or timed out. You can type any city into the search box.');
        setHeroLoading(false);
      },
      { timeout: 8000 }
    );
  };

  // Save Locations Watchdog Handlers
  const handleAddLocation = async (locName) => {
    try {
      await fetch('/api/saved-locations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location: locName })
      });
      fetchSavedLocations();
    } catch (e) {
      console.warn(e);
    }
  };

  const handleDeleteLocation = async (locName) => {
    try {
      await fetch(`/api/saved-locations/${encodeURIComponent(locName)}`, {
        method: 'DELETE'
      });
      fetchSavedLocations();
    } catch (e) {
      console.warn(e);
    }
  };

  // Save LLM Config
  const handleSaveLLM = async (provider, apiKey) => {
    try {
      await fetch('/api/config/llm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, api_key: apiKey })
      });
      setLlmProvider(provider);
    } catch (e) {
      console.warn(e);
    }
  };

  // Parse inline markdown formatting (bold, links, code)
  const parseInlineFormatting = (text) => {
    if (!text) return text;
    const parts = text.split(/(\*\*.*?\*\*)/g).map((part, idx) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={idx}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
    return parts;
  };

  // Full Markdown renderer supporting tables, bullet lists, and paragraphs
  const renderMessageText = (txt) => {
    if (!txt) return null;

    const lines = txt.split('\n');
    const elements = [];
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];

      // Detect start of Markdown Table (consecutive lines starting and ending with '|')
      if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
        const tableLines = [];
        while (i < lines.length && lines[i].trim().startsWith('|') && lines[i].trim().endsWith('|')) {
          tableLines.push(lines[i].trim());
          i++;
        }

        if (tableLines.length >= 2) {
          // Parse header row
          const headerCells = tableLines[0]
            .split('|')
            .slice(1, -1)
            .map((c) => c.trim());

          // Skip separator row (contains '---')
          const isSep = tableLines[1].includes('---');
          const bodyLines = isSep ? tableLines.slice(2) : tableLines.slice(1);

          elements.push(
            <div key={`tbl_${i}`} className="md-table-wrap">
              <table className="md-table">
                <thead>
                  <tr>
                    {headerCells.map((h, hIdx) => (
                      <th key={hIdx}>{parseInlineFormatting(h)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {bodyLines.map((bLine, rIdx) => {
                    const cells = bLine
                      .split('|')
                      .slice(1, -1)
                      .map((c) => c.trim());
                    return (
                      <tr key={rIdx}>
                        {cells.map((cell, cIdx) => (
                          <td key={cIdx}>{parseInlineFormatting(cell)}</td>
                        ))}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          );
          continue;
        }
      }

      // Bullet lists
      if (line.trim().startsWith('• ') || line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        const content = line.trim().replace(/^[•\-\*]\s+/, '');
        elements.push(
          <li key={`li_${i}`} style={{ marginLeft: '16px', marginBottom: '4px' }}>
            {parseInlineFormatting(content)}
          </li>
        );
        i++;
        continue;
      }

      // Paragraphs
      if (line.trim()) {
        elements.push(
          <p key={`p_${i}`} style={{ marginBottom: '6px' }}>
            {parseInlineFormatting(line)}
          </p>
        );
      }
      i++;
    }

    return elements;
  };

  return (
    <div className="app-container">
      {/* Radiant Glowing Background */}
      <div className="ambient-glow glow-1"></div>
      <div className="ambient-glow glow-2"></div>

      {/* Header */}
      <Header
        language={language}
        onLanguageChange={setLanguage}
        voiceEnabled={voiceEnabled}
        onToggleVoice={() => setVoiceEnabled(!voiceEnabled)}
        onOpenSettings={() => setIsSettingsOpen(true)}
        llmProvider={llmProvider}
        watchdogCount={savedLocations.length}
        activeAlertCount={activeHazard ? 1 : 0}
      />

      {/* Extreme Weather Hazard Banner */}
      <HazardAlertBanner
        alert={activeHazard}
        onDismiss={() => setActiveHazard(null)}
      />

      {/* Fixed Location Weather Hero Widget (Apple Weather Style) */}
      <FixedWeatherHero
        heroData={heroData}
        loading={heroLoading}
        onCityChange={handleCityChange}
        onGPSClick={handleGPSClick}
      />

      {/* Main Workspace Layout */}
      <main className="main-layout">
        {/* Chat Section */}
        <section className="chat-section">
          <div className="chat-header">
            <div className="chat-title-wrap">
              <h2>Agentic Meteorological Dialogue</h2>
              <span className="agent-tag">Multi-Agent System</span>
            </div>
            <button
              className="btn-ghost"
              onClick={() => setMessages([])}
              title="Clear Conversation"
            >
              🔄 Clear
            </button>
          </div>

          {/* Messages Stream */}
          <div className="chat-messages">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`message-card ${
                  msg.sender === 'user' ? 'user-message' : 'assistant-message'
                }`}
              >
                <div className="avatar-col">
                  <div className={msg.sender === 'user' ? 'user-avatar' : 'assistant-avatar'}>
                    {msg.sender === 'user' ? '👤' : '🤖'}
                  </div>
                </div>

                <div className="message-body">
                  <div className="message-sender">
                    <div className="sender-left">
                      <span>{msg.sender === 'user' ? 'You' : 'WeatherGPT Agent'}</span>
                      {msg.sender !== 'user' && (
                        <span className="badge-tag">Verified Tool Dispatch</span>
                      )}
                    </div>
                  </div>

                  <div className="message-text">
                    {renderMessageText(msg.text)}
                  </div>

                  {/* Weather Telemetry & Daily Forecast Cards */}
                  {msg.weather_card && (
                    <WeatherTelemetryGrid
                      weather={msg.weather_card}
                      forecast={msg.forecast_data}
                    />
                  )}

                  {/* Hourly 24-hr Chart.js Curve */}
                  {msg.forecast_data?.hourly_chart && (
                    <HourlyChart hourlyData={msg.forecast_data.hourly_chart} />
                  )}

                  {/* Agro Crop Advisory Card */}
                  {msg.advisory_data && (
                    <AgroAdvisoryCard advisory={msg.advisory_data} />
                  )}

                  {/* COMPULSORY ADD-ON: Tool-Selection Trace Panel */}
                  {msg.trace && <ToolTraceCard trace={msg.trace} />}

                  {/* Audio Readout Button */}
                  {msg.sender !== 'user' && (
                    <div className="msg-actions">
                      <button
                        className="btn-audio-speak"
                        onClick={() =>
                          speakText(
                            msg.voice_summary || msg.text.replace(/[*#]/g, ''),
                            msg.language || language
                          )
                        }
                        title="Listen to audio readout"
                      >
                        <span>🔊 Read Out</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="typing-indicator">
                <div className="typing-bubble">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
                <span className="typing-text">
                  Supervisor analyzing intent & orchestrating meteorological tools...
                </span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input Container */}
          <div className="chat-input-container">
            <button
              className={`mic-btn ${isRecording ? 'recording' : ''}`}
              onClick={toggleSpeechRecognition}
              title="Voice Input (Speech-to-Text for Rural Accessibility)"
            >
              🎙️
            </button>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="chat-form"
            >
              <input
                type="text"
                placeholder="Ask weather, crop advisory, forecast... (e.g. 'Will it rain tomorrow in Pune?')"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
              />
              <button type="submit" className="send-btn">
                <span>Send</span>
                <span>➤</span>
              </button>
            </form>
          </div>
        </section>

        {/* Sidebar */}
        <Sidebar
          onSelectPrompt={(query, lang) => {
            if (lang) setLanguage(lang);
            handleSendMessage(query, lang);
          }}
          savedLocations={savedLocations}
          onAddLocation={handleAddLocation}
          onDeleteLocation={handleDeleteLocation}
          onCheckWatchdog={checkWatchdog}
        />
      </main>

      {/* LLM Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        currentProvider={llmProvider}
        onSave={handleSaveLLM}
      />
    </div>
  );
}
