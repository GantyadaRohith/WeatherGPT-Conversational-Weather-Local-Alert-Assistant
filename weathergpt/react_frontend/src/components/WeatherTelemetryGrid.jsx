import React from 'react';

export default function WeatherTelemetryGrid({ weather, forecast }) {
  const daily = forecast?.daily_forecast || [];

  return (
    <div>
      {/* Real-time Telemetry Grid */}
      {weather && (
        <div className="weather-telemetry-grid">
          <div className="telemetry-pill">
            <span className="tel-label">Temp / Feels</span>
            <span className="tel-val">
              {weather.temperature}°C{' '}
              <small style={{ fontSize: '10px', color: '#94a3b8' }}>({weather.feels_like}°)</small>
            </span>
          </div>
          <div className="telemetry-pill">
            <span className="tel-label">Condition</span>
            <span className="tel-val">
              {weather.icon} {weather.condition}
            </span>
          </div>
          <div className="telemetry-pill">
            <span className="tel-label">Humidity</span>
            <span className="tel-val">{weather.humidity}%</span>
          </div>
          <div className="telemetry-pill">
            <span className="tel-label">Wind Speed</span>
            <span className="tel-val">{weather.wind_speed} km/h</span>
          </div>
        </div>
      )}

      {/* Multi-Day Forecast Cards */}
      {daily.length > 0 && (
        <div className="forecast-cards-row">
          {daily.map((d, idx) => (
            <div key={idx} className="f-card">
              <div className="f-date">{d.date.slice(5)}</div>
              <div className="f-icon">{d.icon}</div>
              <div className="f-temp">
                {Math.round(d.temp_max)}° / {Math.round(d.temp_min)}°
              </div>
              <div className="f-rain">🌧️ {d.precip_prob}%</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
