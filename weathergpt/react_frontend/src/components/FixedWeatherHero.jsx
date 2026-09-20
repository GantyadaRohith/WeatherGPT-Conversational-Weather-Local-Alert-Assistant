import React, { useState } from 'react';

export default function FixedWeatherHero({
  heroData,
  loading,
  onCityChange,
  onGPSClick
}) {
  const [searchInput, setSearchInput] = useState('');

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      onCityChange(searchInput.trim());
      setSearchInput('');
    }
  };

  if (!heroData || loading) {
    return (
      <div className="fixed-weather-hero">
        <div className="hero-top-row">
          <div className="hero-location-info">
            <span className="hero-pin-icon">📍</span>
            <div className="hero-city-name">Loading Fixed Weather...</div>
          </div>
        </div>
      </div>
    );
  }

  const loc = heroData.location || { name: 'New Delhi', admin1: 'Delhi' };
  const curr = heroData.current || {};
  const timeline = heroData.hourly_timeline || [];

  return (
    <div className="fixed-weather-hero">
      <div className="hero-glow-accent"></div>

      {/* Top Row: Location Name + Search / GPS */}
      <div className="hero-top-row">
        <div className="hero-location-info">
          <span className="hero-pin-icon">📍</span>
          <div>
            <div className="hero-city-name">
              {loc.name}
              <span className="hero-state-tag">{loc.admin1 || loc.country || 'India'}</span>
            </div>
          </div>
        </div>

        <div className="hero-city-search-bar">
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '8px' }}>
            <input
              type="text"
              className="hero-search-input"
              placeholder="Change pinned city (e.g. Pune)..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
          </form>
          <button
            type="button"
            className="btn-gps"
            onClick={onGPSClick}
            title="Use current device GPS location"
          >
            🎯
          </button>
        </div>
      </div>

      {/* Center Content Grid: Big Temp Column | Hourly Scroller | Telemetry Mini Grid */}
      <div className="hero-content-grid">
        
        {/* Big Temperature & Condition Column */}
        <div className="hero-temp-column">
          <span className="hero-weather-icon">{curr.icon || '⛅'}</span>
          <div>
            <div className="hero-temp-big">{Math.round(curr.temperature || 25)}°C</div>
            <div className="hero-condition-wrap">
              <span className="hero-condition-text">{curr.condition || 'Clear'}</span>
              <span className="hero-range-text">
                Feels like {Math.round(curr.feels_like || curr.temperature || 25)}° • H: {Math.round(heroData.daily_high || curr.temperature || 28)}° L: {Math.round(heroData.daily_low || curr.temperature || 18)}°
              </span>
            </div>
          </div>
        </div>

        {/* Hourly Forecast Timeline (Apple Weather Style) */}
        <div className="hero-hourly-scroller">
          {timeline.map((item, idx) => (
            <div key={idx} className="hourly-pill-item">
              <span className="hourly-time">{item.time}</span>
              <span className="hourly-icon">{item.icon}</span>
              <span className="hourly-temp">{item.temp}°</span>
              <span className="hourly-rain">{item.rain_prob > 0 ? `💧${item.rain_prob}%` : '•'}</span>
            </div>
          ))}
        </div>

        {/* Telemetry Mini-Grid */}
        <div className="hero-telemetry-mini">
          <div className="h-tel-card">
            <span>Humidity</span>
            <strong>{curr.humidity || 55}%</strong>
          </div>
          <div className="h-tel-card">
            <span>Wind</span>
            <strong>{curr.wind_speed || 8} km/h</strong>
          </div>
          <div className="h-tel-card">
            <span>UV Index</span>
            <strong>{curr.uv_index || 4} ({heroData.uv_category || 'Mod'})</strong>
          </div>
          <div className="h-tel-card">
            <span>Air Pressure</span>
            <strong>{Math.round(curr.surface_pressure || 1012)} hPa</strong>
          </div>
        </div>

      </div>
    </div>
  );
}
