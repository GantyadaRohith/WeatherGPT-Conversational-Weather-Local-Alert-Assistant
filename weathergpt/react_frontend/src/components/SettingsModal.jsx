import { API_BASE_URL } from '../config';
import React, { useState, useEffect } from 'react';

export default function SettingsModal({
  isOpen,
  onClose,
  currentProvider,
  onSave
}) {
  const [activeTab, setActiveTab] = useState('llm'); // 'llm', 'database', 'notifications'
  
  // LLM State
  const [provider, setProvider] = useState(currentProvider || 'local');
  const [apiKey, setApiKey] = useState('');
  
  // Database State
  const [dbStatus, setDbStatus] = useState(null);
  const [mongoUri, setMongoUri] = useState('');
  const [mongoDb, setMongoDb] = useState('weathergpt');

  // Notification Credentials State
  const [notifStatus, setNotifStatus] = useState(null);
  const [twilioSid, setTwilioSid] = useState('');
  const [twilioToken, setTwilioToken] = useState('');
  const [twilioPhone, setTwilioPhone] = useState('');
  const [whatsappToken, setWhatsappToken] = useState('');
  const [whatsappPhoneId, setWhatsappPhoneId] = useState('');

  const [statusMsg, setStatusMsg] = useState('');

  useEffect(() => {
    if (isOpen) {
      // Fetch DB & Notif status
      fetch(`${API_BASE_URL}/api/database/status`)
        .then(r => r.json())
        .then(data => setDbStatus(data))
        .catch(console.warn);

      fetch(`${API_BASE_URL}/api/notifications/status`)
        .then(r => r.json())
        .then(data => setNotifStatus(data))
        .catch(console.warn);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSaveLLM = async (e) => {
    e.preventDefault();
    await onSave(provider, apiKey);
    setStatusMsg('LLM Engine updated successfully!');
    setTimeout(() => setStatusMsg(''), 2000);
  };

  const handleSaveNotifConfig = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/api/notifications/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          twilio_account_sid: twilioSid || undefined,
          twilio_auth_token: twilioToken || undefined,
          twilio_phone_number: twilioPhone || undefined,
          whatsapp_token: whatsappToken || undefined,
          whatsapp_phone_number_id: whatsappPhoneId || undefined
        })
      });
      if (res.ok) {
        setStatusMsg('Notification keys saved successfully!');
        const sRes = await fetch(`${API_BASE_URL}/api/notifications/status`);
        if (sRes.ok) setNotifStatus(await sRes.json());
        setTimeout(() => setStatusMsg(''), 2000);
      }
    } catch (err) {
      alert(`Error saving credentials: ${err.message}`);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card settings-modal-card">
        <div className="modal-header">
          <div className="modal-title-wrap">
            <span className="modal-icon">⚙️</span>
            <div>
              <h3>System Settings & Integration Hub</h3>
              <small style={{ color: '#94a3b8' }}>Multi-Agent LLMs · MongoDB Persistence · Twilio & WhatsApp</small>
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        {/* Tab Selection */}
        <div className="modal-tabs">
          <button
            className={`tab-btn ${activeTab === 'llm' ? 'active' : ''}`}
            onClick={() => setActiveTab('llm')}
          >
            🧠 AI Reasoning Engine
          </button>
          <button
            className={`tab-btn ${activeTab === 'database' ? 'active' : ''}`}
            onClick={() => setActiveTab('database')}
          >
            🍃 Database (MongoDB)
          </button>
          <button
            className={`tab-btn ${activeTab === 'notifications' ? 'active' : ''}`}
            onClick={() => setActiveTab('notifications')}
          >
            📱 Twilio & WhatsApp API
          </button>
        </div>

        <div className="modal-body">
          {/* TAB 1: LLM CONFIG */}
          {activeTab === 'llm' && (
            <form onSubmit={handleSaveLLM}>
              <div className="form-group">
                <label>Select Multi-Agent Reasoning Engine:</label>
                <div className="provider-cards-grid">
                  <div
                    className={`provider-card ${provider === 'local' ? 'selected' : ''}`}
                    onClick={() => setProvider('local')}
                  >
                    <strong>Local Smart Agent</strong>
                    <small>Built-in Heuristic & Semantic Engine (Free, 100% Offline, Zero-Key)</small>
                  </div>

                  <div
                    className={`provider-card ${provider === 'groq' ? 'selected' : ''}`}
                    onClick={() => setProvider('groq')}
                  >
                    <strong>Groq Cloud</strong>
                    <small>Llama 3.3 70B / OSS (Ultra-fast LLM tool synthesis)</small>
                  </div>

                  <div
                    className={`provider-card ${provider === 'gemini' ? 'selected' : ''}`}
                    onClick={() => setProvider('gemini')}
                  >
                    <strong>Google Gemini</strong>
                    <small>Gemini 1.5 Flash (Multilingual & Indian dialect reasoning)</small>
                  </div>

                  <div
                    className={`provider-card ${provider === 'openai' ? 'selected' : ''}`}
                    onClick={() => setProvider('openai')}
                  >
                    <strong>OpenAI</strong>
                    <small>GPT-4o Mini (Cloud Hosted API)</small>
                  </div>
                </div>
              </div>

              {provider !== 'local' && (
                <div className="form-group">
                  <label>API Key for {provider.toUpperCase()}:</label>
                  <input
                    type="password"
                    className="form-input"
                    placeholder={`Enter your ${provider} API key...`}
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                  />
                  <small style={{ color: '#94a3b8', fontSize: '11px' }}>
                    Key is sent securely to the local backend session and never logged.
                  </small>
                </div>
              )}

              {statusMsg && (
                <div className="settings-status-alert">✓ {statusMsg}</div>
              )}

              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={onClose}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save Engine
                </button>
              </div>
            </form>
          )}

          {/* TAB 2: DATABASE CONFIG */}
          {activeTab === 'database' && (
            <div className="db-config-section">
              <div className="db-status-banner">
                <div className="db-status-icon">
                  {dbStatus?.engine === 'mongodb' ? '🍃' : '💾'}
                </div>
                <div>
                  <h4>Current Storage Engine: <strong>{dbStatus?.engine === 'mongodb' ? 'MongoDB Atlas / Instance' : 'Persistent JSON Document Store'}</strong></h4>
                  <p style={{ color: '#94a3b8', fontSize: '12px' }}>
                    Status: <span style={{ color: '#10b981', fontWeight: 600 }}>{dbStatus?.status || 'Active'}</span>
                    {dbStatus?.database && ` · Database: ${dbStatus.database}`}
                  </p>
                </div>
              </div>

              <div className="db-stats-grid">
                <div className="db-stat-box">
                  <span className="stat-label">Saved Hubs</span>
                  <span className="stat-num">{dbStatus?.counts?.saved_locations || 0}</span>
                </div>
                <div className="db-stat-box">
                  <span className="stat-label">Alert Dispatches</span>
                  <span className="stat-num">{dbStatus?.counts?.alert_dispatches || 0}</span>
                </div>
                <div className="db-stat-box">
                  <span className="stat-label">Subscribers</span>
                  <span className="stat-num">{dbStatus?.counts?.subscribers || 0}</span>
                </div>
              </div>

              <div className="form-group" style={{ marginTop: '16px' }}>
                <label>MongoDB Connection URI (Optional):</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="mongodb+srv://username:password@cluster.mongodb.net/weathergpt"
                  value={mongoUri}
                  onChange={(e) => setMongoUri(e.target.value)}
                />
                <small style={{ color: '#94a3b8', fontSize: '11px' }}>
                  If not provided or unconfigured, WeatherGPT uses the zero-crash persistent JSON document store (<code>weathergpt_db.json</code>) which guarantees full persistence across server restarts.
                </small>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={onClose}>
                  Close
                </button>
              </div>
            </div>
          )}

          {/* TAB 3: TWILIO & WHATSAPP CONFIG */}
          {activeTab === 'notifications' && (
            <form onSubmit={handleSaveNotifConfig} className="notif-config-form">
              <div className="notif-status-summary">
                <div className="status-item">
                  <span>Twilio SMS:</span>
                  <span className={`badge-pill ${notifStatus?.twilio_sms?.configured ? 'configured' : 'simulation'}`}>
                    {notifStatus?.twilio_sms?.configured ? '✓ Configured' : '⚡ Evaluator Simulation'}
                  </span>
                </div>
                <div className="status-item">
                  <span>WhatsApp Cloud API:</span>
                  <span className={`badge-pill ${notifStatus?.whatsapp_cloud_api?.configured ? 'configured' : 'simulation'}`}>
                    {notifStatus?.whatsapp_cloud_api?.configured ? '✓ Configured' : '⚡ Evaluator Simulation'}
                  </span>
                </div>
              </div>

              <h4 style={{ color: '#38bdf8', fontSize: '13px', margin: '12px 0 8px' }}>Twilio REST API Configuration</h4>
              <div className="form-row-grid">
                <div className="form-group">
                  <label>Twilio Account SID:</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
                    value={twilioSid}
                    onChange={(e) => setTwilioSid(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Twilio Auth Token:</label>
                  <input
                    type="password"
                    className="form-input"
                    placeholder="••••••••••••••••••••••••••••••••"
                    value={twilioToken}
                    onChange={(e) => setTwilioToken(e.target.value)}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Twilio Sender Phone Number:</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="+1234567890"
                  value={twilioPhone}
                  onChange={(e) => setTwilioPhone(e.target.value)}
                />
              </div>

              <h4 style={{ color: '#34d399', fontSize: '13px', margin: '14px 0 8px' }}>Meta WhatsApp Cloud API Configuration</h4>
              <div className="form-row-grid">
                <div className="form-group">
                  <label>WhatsApp Cloud Access Token:</label>
                  <input
                    type="password"
                    className="form-input"
                    placeholder="EAABwz..."
                    value={whatsappToken}
                    onChange={(e) => setWhatsappToken(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Phone Number ID:</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="1029384756..."
                    value={whatsappPhoneId}
                    onChange={(e) => setWhatsappPhoneId(e.target.value)}
                  />
                </div>
              </div>

              {statusMsg && (
                <div className="settings-status-alert">✓ {statusMsg}</div>
              )}

              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={onClose}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save Credentials
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
