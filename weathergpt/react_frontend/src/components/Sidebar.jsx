import React, { useState } from 'react';

export default function Sidebar({
  onSelectPrompt,
  savedLocations,
  onAddLocation,
  onDeleteLocation,
  onCheckWatchdog
}) {
  const [newCity, setNewCity] = useState('');

  const handleAddSubmit = (e) => {
    e.preventDefault();
    if (newCity.trim()) {
      onAddLocation(newCity.trim());
      setNewCity('');
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

      {/* Saved Locations Watchdog */}
      <div className="glass-card">
        <div className="card-header">
          <h3>📍 Saved Location Watchdog</h3>
          <button className="btn-xs" onClick={onCheckWatchdog}>Check Now</button>
        </div>
        <p className="card-desc">Automated threshold monitor for saved farmer & city hubs:</p>

        <div className="saved-locations-list">
          {savedLocations.map((loc, idx) => (
            <div key={idx} className="saved-loc-item">
              <div className="loc-info">
                <strong>{loc.location}</strong>
                <small>Threshold: {loc.threshold_rain_mm}mm rain</small>
              </div>
              <div className="loc-actions">
                <span className="loc-status-pill">Monitoring</span>
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

        <form onSubmit={handleAddSubmit} className="add-loc-form">
          <input
            type="text"
            placeholder="Add city (e.g. Patna)"
            value={newCity}
            onChange={(e) => setNewCity(e.target.value)}
            required
          />
          <button type="submit" className="btn-add">+</button>
        </form>
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
