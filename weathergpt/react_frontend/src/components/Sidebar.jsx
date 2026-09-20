import React, { useState } from 'react';

export default function Sidebar({
  onSelectPrompt,
  savedLocations,
  onAddLocation,
  onDeleteLocation,
  onCheckWatchdog,
  onOpenDispatcher,
  onOpenSubscriber,
  dbStatus
}) {
  const [newCity, setNewCity] = useState('');
  const [newPhone, setNewPhone] = useState('+919876543210');
  const [newChannel, setNewChannel] = useState('whatsapp');
  const [showAddForm, setShowAddForm] = useState(false);

  const handleAddSubmit = (e) => {
    e.preventDefault();
    if (newCity.trim()) {
      onAddLocation(newCity.trim(), 25.0, newPhone.trim(), newChannel);
      setNewCity('');
      setShowAddForm(false);
    }
  };

  return (
    <aside className="sidebar-section">
      {/* Evaluator Quick Test Bench */}
      <div className="glass-card">
        <div className="card-header">
          <h3>⚡ Evaluator Quick Test Bench</h3>
          <span className="badge-mini">All 5 Tools</span>
        </div>
        <p className="card-desc">Click any test case to verify agent tool-selection and execution traces:</p>
        
        <div className="quick-prompts-grid">
          <button
            className="quick-btn"
            onClick={() => onSelectPrompt('Current weather and humidity in Mumbai', 'en')}
          >
            <span className="qb-icon">🌡️</span>
            <div className="qb-text">
              <strong>Current Weather</strong>
              <small>Tool: get_current_weather</small>
            </div>
          </button>

          <button
            className="quick-btn"
            onClick={() => onSelectPrompt('Will it rain tomorrow in Varanasi? Give 5-day forecast', 'en')}
          >
            <span className="qb-icon">📅</span>
            <div className="qb-text">
              <strong>Multi-Day Forecast</strong>
              <small>Tool: get_forecast</small>
            </div>
          </button>

          <button
            className="quick-btn"
            onClick={() => onSelectPrompt('Can I spray pesticide on cotton crops in Nagpur this week?', 'en')}
          >
            <span className="qb-icon">🌾</span>
            <div className="qb-text">
              <strong>Farmer Crop Advisory</strong>
              <small>Tool: get_crop_advisory</small>
            </div>
          </button>

          <button
            className="quick-btn"
            onClick={() => onSelectPrompt('Compare Delhi temperature today vs last year historical climate', 'en')}
          >
            <span className="qb-icon">📊</span>
            <div className="qb-text">
              <strong>Climate Anomaly</strong>
              <small>Tool: get_historical_climate</small>
            </div>
          </button>

          <button
            className="quick-btn"
            onClick={() => onSelectPrompt('Simulate extreme cyclone alert test for Chennai', 'en')}
          >
            <span className="qb-icon">🚨</span>
            <div className="qb-text">
              <strong>Disaster Warning</strong>
              <small>Tool: get_severe_alerts</small>
            </div>
          </button>

          <button
            className="quick-btn"
            onClick={() => onSelectPrompt('वाराणसी में आज का मौसम कैसा है?', 'hi')}
          >
            <span className="qb-icon">🇮🇳</span>
            <div className="qb-text">
              <strong>हिन्दी (Hindi Test)</strong>
              <small>Multilingual Query</small>
            </div>
          </button>
        </div>
      </div>

      {/* Database & Notification Engine Card */}
      <div className="glass-card db-card">
        <div className="card-header">
          <h3>💾 Database & Alerts</h3>
          <span className="badge-mini-green">
            {dbStatus?.engine === 'mongodb' ? '🍃 MongoDB' : 'Persistent Store'}
          </span>
        </div>
        <p className="card-desc">Audit trail for alerts & community subscribers:</p>

        <div className="db-summary-grid">
          <div className="db-sum-item">
            <span className="sum-label">Logged Dispatches</span>
            <span className="sum-val">{dbStatus?.counts?.alert_dispatches || 0}</span>
          </div>
          <div className="db-sum-item">
            <span className="sum-label">Monitored Hubs</span>
            <span className="sum-val">{savedLocations.length}</span>
          </div>
        </div>

        <div className="db-card-buttons">
          <button className="btn-sidebar-action" onClick={onOpenDispatcher}>
            📜 View Dispatch Logs
          </button>
          <button className="btn-sidebar-action secondary" onClick={onOpenSubscriber}>
            ➕ Subscribe Alerts
          </button>
        </div>
      </div>

      {/* Saved Locations Watchdog (MongoDB Backed) */}
      <div className="glass-card">
        <div className="card-header">
          <h3>📍 Saved Location Watchdog</h3>
          <button className="btn-xs" onClick={onCheckWatchdog}>Check Now</button>
        </div>
        <p className="card-desc">Scheduled 60s monitor evaluating hazard thresholds:</p>

        <div className="saved-locations-list">
          {savedLocations.map((loc, idx) => (
            <div key={idx} className="saved-loc-item">
              <div className="loc-info">
                <div className="loc-title-row">
                  <strong>{loc.location}</strong>
                  <span className={`channel-pill ${loc.channel || 'whatsapp'}`}>
                    {loc.channel === 'sms' ? '🔵 SMS' : '🟢 WhatsApp'}
                  </span>
                </div>
                <small>Threshold: {loc.threshold_rain_mm || 25}mm rain · {loc.phone || 'Alerts Active'}</small>
              </div>
              <div className="loc-actions">
                <button
                  className="btn-del-loc"
                  onClick={() => onDeleteLocation(loc.location)}
                  title="Remove location"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>

        {!showAddForm ? (
          <button
            type="button"
            className="btn-show-add"
            onClick={() => setShowAddForm(true)}
          >
            + Add Monitored Hub
          </button>
        ) : (
          <form onSubmit={handleAddSubmit} className="add-loc-expand-form">
            <input
              type="text"
              placeholder="City (e.g. Hyderabad)"
              value={newCity}
              onChange={(e) => setNewCity(e.target.value)}
              required
            />
            <div className="form-sub-row">
              <input
                type="text"
                placeholder="Phone (+91...)"
                value={newPhone}
                onChange={(e) => setNewPhone(e.target.value)}
              />
              <select
                value={newChannel}
                onChange={(e) => setNewChannel(e.target.value)}
              >
                <option value="whatsapp">WhatsApp</option>
                <option value="sms">SMS</option>
              </select>
            </div>
            <div className="add-actions-row">
              <button type="submit" className="btn-add-confirm">Save Hub</button>
              <button type="button" className="btn-cancel-mini" onClick={() => setShowAddForm(false)}>Cancel</button>
            </div>
          </form>
        )}
      </div>

      {/* Atmospheric Radar Simulation */}
      <div className="glass-card">
        <div className="card-header">
          <h3>📡 Atmospheric Doppler Radar</h3>
          <span className="radar-live-tag">LIVE SCAN</span>
        </div>
        <div className="radar-display">
          <div className="radar-sweep"></div>
          <div className="radar-grid"></div>
          <div className="radar-blip blip-1"></div>
          <div className="radar-blip blip-2"></div>
          <div className="radar-info-overlay">
            <span>INSAT-3D Doppler Composite</span>
            <span>Coverage: Indian Subcontinent</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
