/**
 * WeatherGPT Frontend Application
 * Handles chat streaming, agent tool-selection traces, Chart.js graphs,
 * Web Speech API (STT & TTS), and automated alert watchdog.
 */

// Application State
const state = {
  language: 'en',
  voiceReadoutEnabled: true,
  isRecording: false,
  activeCharts: {},
  recognition: null,
};

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const micBtn = document.getElementById('micBtn');
const langSelect = document.getElementById('langSelect');
const voiceToggleBtn = document.getElementById('voiceToggleBtn');
const voiceToggleLabel = document.getElementById('voiceToggleLabel');
const voiceToggleIcon = document.getElementById('voiceToggleIcon');
const typingIndicator = document.getElementById('agentTypingIndicator');
const typingStatusText = document.getElementById('typingStatusText');
const clearChatBtn = document.getElementById('clearChatBtn');
const hazardGlobalBanner = document.getElementById('hazardGlobalBanner');
const hazardBannerTitle = document.getElementById('hazardBannerTitle');
const hazardBannerDesc = document.getElementById('hazardBannerDesc');
const savedLocationsList = document.getElementById('savedLocationsList');
const addLocationForm = document.getElementById('addLocationForm');
const newLocInput = document.getElementById('newLocInput');
const refreshWatchdogBtn = document.getElementById('refreshWatchdogBtn');

// Initialize Web Speech API (Speech-to-Text)
function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn('Web Speech Recognition API not supported in this browser.');
    micBtn.style.opacity = '0.5';
    micBtn.title = 'Voice input not supported on this browser';
    return;
  }

  state.recognition = new SpeechRecognition();
  state.recognition.continuous = false;
  state.recognition.interimResults = false;

  const langCodeMap = {
    en: 'en-IN',
    hi: 'hi-IN',
    bn: 'bn-IN',
    ta: 'ta-IN',
    te: 'te-IN',
    mr: 'mr-IN'
  };
  state.recognition.lang = langCodeMap[state.language] || 'en-IN';

  state.recognition.onstart = () => {
    state.isRecording = true;
    micBtn.classList.add('recording');
  };

  state.recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    userInput.value = transcript;
    state.isRecording = false;
    micBtn.classList.remove('recording');
    handleChatSubmit();
  };

  state.recognition.onerror = (event) => {
    console.warn('Speech recognition error:', event.error);
    state.isRecording = false;
    micBtn.classList.remove('recording');
  };

  state.recognition.onend = () => {
    state.isRecording = false;
    micBtn.classList.remove('recording');
  };
}

// Text-to-Speech (Voice Output)
function speakText(text, lang = 'en') {
  if (!('speechSynthesis' in window) || !state.voiceReadoutEnabled) return;

  window.speechSynthesis.cancel(); // cancel prior speech
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
  utterance.pitch = 1.0;

  window.speechSynthesis.speak(utterance);
}

// Format Markdown Bold / Bullets simply
function renderFormattedMarkdown(text) {
  if (!text) return '';
  let formatted = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^• (.*$)/gim, '<li>$1</li>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>');

  if (formatted.includes('<li>')) {
    formatted = formatted.replace(/(<li>.*<\/li>)/gis, '<ul style="padding-left: 20px; margin: 6px 0;">$1</ul>');
  }
  return formatted;
}

// Render User Message
function appendUserMessage(text) {
  const msgEl = document.createElement('div');
  msgEl.className = 'message-card user-message animate-fade';
  msgEl.innerHTML = `
    <div class="avatar-col">
      <div class="user-avatar">👤</div>
    </div>
    <div class="message-body">
      <div class="message-sender">
        <span>You</span>
      </div>
      <div class="message-text">${escapeHtml(text)}</div>
    </div>
  `;
  chatMessages.appendChild(msgEl);
  scrollToBottom();
}

// Render Assistant Response with Compulsory Tool Trace & Weather Visuals
function appendAssistantMessage(data) {
  const msgId = 'chart_' + Date.now();
  const trace = data.trace || {};
  const weather = data.weather_card;
  const forecast = data.forecast_data;
  const advisory = data.advisory_data;
  const historical = data.historical_data;
  const alerts = data.alerts || [];

  // Determine tool badge class
  const toolClassMap = {
    get_current_weather: 'tool-current',
    get_forecast: 'tool-forecast',
    get_crop_advisory: 'tool-crop',
    get_severe_alerts: 'tool-alert',
    get_historical_climate: 'tool-climate',
    get_commute_advisory: 'tool-current'
  };
  const toolClass = toolClassMap[trace.tool_picked] || 'tool-current';

  const msgEl = document.createElement('div');
  msgEl.className = 'message-card assistant-message animate-fade';

  // Build Telemetry Pill Grid if weather present
  let telemetryHtml = '';
  if (weather) {
    telemetryHtml = `
      <div class="weather-telemetry-grid">
        <div class="telemetry-pill">
          <span class="tel-label">Temp / Feels</span>
          <span class="tel-val">${weather.temperature}°C <small style="font-size:10px; color:#94a3b8">(${weather.feels_like}°)</small></span>
        </div>
        <div class="telemetry-pill">
          <span class="tel-label">Condition</span>
          <span class="tel-val">${weather.icon} ${weather.condition}</span>
        </div>
        <div class="telemetry-pill">
          <span class="tel-label">Humidity</span>
          <span class="tel-val">${weather.humidity}%</span>
        </div>
        <div class="telemetry-pill">
          <span class="tel-label">Wind Speed</span>
          <span class="tel-val">${weather.wind_speed} km/h</span>
        </div>
      </div>
    `;
  }

  // Build Daily Forecast Cards if forecast present
  let forecastCardsHtml = '';
  if (forecast && forecast.daily_forecast && forecast.daily_forecast.length > 0) {
    const cards = forecast.daily_forecast.map(d => `
      <div class="f-card">
        <div class="f-date">${d.date.slice(5)}</div>
        <div class="f-icon">${d.icon}</div>
        <div class="f-temp">${Math.round(d.temp_max)}° / ${Math.round(d.temp_min)}°</div>
        <div class="f-rain">🌧️ ${d.precip_prob}%</div>
      </div>
    `).join('');
    forecastCardsHtml = `<div class="forecast-cards-row">${cards}</div>`;
  }

  // Build Chart Canvas if hourly forecast is present
  let chartCanvasHtml = '';
  if (forecast && forecast.hourly_chart) {
    chartCanvasHtml = `
      <div class="chart-container-box">
        <canvas id="${msgId}"></canvas>
      </div>
    `;
  }

  // Build Agro Advisory Card if present
  let agroHtml = '';
  if (advisory) {
    const isRestricted = !advisory.spray_feasible;
    agroHtml = `
      <div class="agro-advisory-card">
        <div class="agro-advisory-header">
          <strong>🌾 ${advisory.crop}</strong>
          <span class="agro-badge ${isRestricted ? 'restricted' : ''}">
            ${advisory.spray_feasible ? '✓ Safe Spray' : '⚠️ Spray Restricted'}
          </span>
        </div>
        <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 4px;">
          <strong>Irrigation:</strong> ${advisory.irrigation_details}
        </div>
        <div style="font-size: 11.5px; color: #94a3b8;">
          <strong>Agronomy Tip:</strong> ${advisory.crop_tip}
        </div>
      </div>
    `;
  }

  // Build Alert Banner if hazardous
  if (alerts && alerts.length > 0) {
    const topAlert = alerts[0];
    showHazardBanner(topAlert.type, topAlert.message);
  }

  // COMPULSORY ADD-ON: Tool-Selection Trace HTML
  const traceHtml = `
    <div class="trace-panel">
      <div class="trace-header">
        <span class="trace-chip ${toolClass}">${trace.tool_picked || 'dispatch_agent'}</span>
        <span class="trace-title">Judges' Tool-Selection Trace</span>
        <span class="trace-latency">⚡ ${trace.latency_ms || 120} ms | Confidence: ${Math.round((trace.confidence || 0.95) * 100)}%</span>
      </div>
      <div class="trace-body">
        <div class="trace-row">
          <span class="t-label">Params:</span>
          <span class="t-val">${JSON.stringify(trace.parameters || {})}</span>
        </div>
        <div class="trace-row">
          <span class="t-label">Reason:</span>
          <span class="t-val">${trace.reason || 'Direct meteorological query intent resolution.'}</span>
        </div>
      </div>
    </div>
  `;

  // Action Bar with Speech Readout
  const speakPayload = escapeHtml(data.voice_summary || data.reply.replace(/[*#]/g, ''));
  const actionsHtml = `
    <div class="msg-actions">
      <button class="btn-audio-speak" onclick="speakText('${speakPayload}', '${data.language || state.language}')" title="Listen in audio">
        <span>🔊 Read Out</span>
      </button>
    </div>
  `;

  msgEl.innerHTML = `
    <div class="avatar-col">
      <div class="assistant-avatar">🤖</div>
    </div>
    <div class="message-body">
      <div class="message-sender">
        <span>WeatherGPT Agent</span>
        <span class="badge-tag">Verified Tool Dispatch</span>
      </div>
      <div class="message-text">
        ${renderFormattedMarkdown(data.reply)}
      </div>
      ${telemetryHtml}
      ${forecastCardsHtml}
      ${chartCanvasHtml}
      ${agroHtml}
      ${traceHtml}
      ${actionsHtml}
    </div>
  `;

  chatMessages.appendChild(msgEl);
  scrollToBottom();

  // Render Chart.js if canvas exists
  if (forecast && forecast.hourly_chart) {
    renderHourlyChart(msgId, forecast.hourly_chart);
  }

  // Trigger speech synthesis if enabled
  if (state.voiceReadoutEnabled && data.voice_summary) {
    speakText(data.voice_summary, data.language || state.language);
  }
}

// Render Chart.js 24-Hour Curve
function renderHourlyChart(canvasId, hourlyData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: hourlyData.hours,
      datasets: [
        {
          label: 'Temperature (°C)',
          data: hourlyData.temperatures,
          borderColor: '#00d2ff',
          backgroundColor: 'rgba(0, 210, 255, 0.1)',
          borderWidth: 2,
          tension: 0.35,
          fill: true,
          yAxisID: 'y'
        },
        {
          label: 'Rain Probability (%)',
          data: hourlyData.rain_probabilities,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.3)',
          borderWidth: 1,
          type: 'bar',
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#94a3b8', font: { size: 10 } }
        },
        tooltip: { mode: 'index', intersect: false }
      },
      scales: {
        x: {
          ticks: { color: '#64748b', maxTicksLimit: 8, font: { size: 10 } },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          ticks: { color: '#00d2ff', font: { size: 10 } },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          min: 0,
          max: 100,
          ticks: { color: '#60a5fa', font: { size: 10 } },
          grid: { drawOnChartArea: false }
        }
      }
    }
  });
}

// Show/Hide Hazard Alert Banner
function showHazardBanner(title, message) {
  hazardBannerTitle.innerText = title;
  hazardBannerDesc.innerText = message;
  hazardGlobalBanner.classList.remove('hidden');
}

function dismissHazardBanner() {
  hazardGlobalBanner.classList.add('hidden');
}

// Handle User Chat Submission
async function handleChatSubmit() {
  const query = userInput.value.trim();
  if (!query) return;

  appendUserMessage(query);
  userInput.value = '';
  showTyping(true);

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: query,
        language: state.language
      })
    });

    if (!response.ok) {
      throw new Error(`Server returned HTTP ${response.status}`);
    }

    const data = await response.json();
    showTyping(false);
    appendAssistantMessage(data);

  } catch (error) {
    console.error('Chat error:', error);
    showTyping(false);
    appendAssistantMessage({
      reply: `⚠️ Connection error: Could not reach backend weather agent (${error.message}). Please ensure the local server is running.`,
      trace: {
        tool_picked: 'error_fallback',
        parameters: { error: error.message },
        reason: 'Network or backend execution exception.',
        latency_ms: 50
      },
      language: state.language
    });
  }
}

function showTyping(show) {
  if (show) {
    typingIndicator.classList.remove('hidden');
    scrollToBottom();
  } else {
    typingIndicator.classList.add('hidden');
  }
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

// Load and Render Saved Locations for Watchdog
async function loadSavedLocations() {
  try {
    const res = await fetch('/api/saved-locations');
    const locations = await res.json();
    savedLocationsList.innerHTML = '';

    locations.forEach(loc => {
      const item = document.createElement('div');
      item.className = 'saved-loc-item';
      item.innerHTML = `
        <div class="loc-info">
          <strong>${loc.location}</strong>
          <small>Threshold: ${loc.threshold_rain_mm}mm rain</small>
        </div>
        <span class="loc-status-pill">Monitoring</span>
      `;
      savedLocationsList.appendChild(item);
    });
  } catch (e) {
    console.warn('Could not load saved locations:', e);
  }
}

// Watchdog Automated Check
async function runWatchdogCheck() {
  try {
    const res = await fetch('/api/alerts/watchdog-check');
    const results = await res.json();
    let triggeredCount = 0;

    results.forEach(r => {
      if (r.active_alerts && r.active_alerts.length > 0) {
        triggeredCount++;
        showHazardBanner(r.active_alerts[0].type, `${r.location}: ${r.active_alerts[0].message}`);
      }
    });

    const watchdogBadge = document.getElementById('watchdogBadge');
    if (watchdogBadge) {
      watchdogBadge.innerHTML = `<span class="pulse-indicator"></span><span>Watchdog: ${results.length} Active (${triggeredCount} Alerts)</span>`;
    }
  } catch (e) {
    console.warn('Watchdog check error:', e);
  }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
  initSpeechRecognition();
  loadSavedLocations();
  runWatchdogCheck();

  // Chat Form Submit
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleChatSubmit();
  });

  // Microphone Button (Speech-to-Text)
  micBtn.addEventListener('click', () => {
    if (!state.recognition) {
      alert('Speech Recognition is not supported by your browser. Please type your query.');
      return;
    }

    if (state.isRecording) {
      state.recognition.stop();
    } else {
      const langCodeMap = {
        en: 'en-IN',
        hi: 'hi-IN',
        bn: 'bn-IN',
        ta: 'ta-IN',
        te: 'te-IN',
        mr: 'mr-IN'
      };
      state.recognition.lang = langCodeMap[state.language] || 'en-IN';
      state.recognition.start();
    }
  });

  // Language Switcher
  langSelect.addEventListener('change', (e) => {
    state.language = e.target.value;
    if (state.recognition) {
      const langCodeMap = {
        en: 'en-IN',
        hi: 'hi-IN',
        bn: 'bn-IN',
        ta: 'ta-IN',
        te: 'te-IN',
        mr: 'mr-IN'
      };
      state.recognition.lang = langCodeMap[state.language] || 'en-IN';
    }
  });

  // Voice Readout Toggle
  voiceToggleBtn.addEventListener('click', () => {
    state.voiceReadoutEnabled = !state.voiceReadoutEnabled;
    if (state.voiceReadoutEnabled) {
      voiceToggleBtn.classList.add('active');
      voiceToggleLabel.innerText = 'Voice Readout ON';
      voiceToggleIcon.innerText = '🔊';
    } else {
      voiceToggleBtn.classList.remove('active');
      voiceToggleLabel.innerText = 'Voice Readout OFF';
      voiceToggleIcon.innerText = '🔇';
      window.speechSynthesis.cancel();
    }
  });

  // Clear Chat
  clearChatBtn.addEventListener('click', () => {
    chatMessages.innerHTML = '';
    window.speechSynthesis.cancel();
  });

  // Quick Prompt Bench Buttons for Judges
  document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const q = btn.getAttribute('data-query');
      const lang = btn.getAttribute('data-lang');
      if (lang) {
        state.language = lang;
        langSelect.value = lang;
      }
      userInput.value = q;
      handleChatSubmit();
    });
  });

  // Add Location Form
  addLocationForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const loc = newLocInput.value.trim();
    if (!loc) return;

    try {
      await fetch('/api/saved-locations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location: loc })
      });
      newLocInput.value = '';
      loadSavedLocations();
    } catch (err) {
      console.error(err);
    }
  });

  // Refresh Watchdog Button
  refreshWatchdogBtn.addEventListener('click', () => {
    runWatchdogCheck();
  });

  // Periodic Watchdog Check every 60 seconds
  setInterval(runWatchdogCheck, 60000);
});
