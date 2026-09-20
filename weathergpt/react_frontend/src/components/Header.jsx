import React from 'react';

export default function Header({
  language,
  onLanguageChange,
  voiceEnabled,
  onToggleVoice,
  onOpenSettings,
  llmProvider,
  watchdogCount,
  activeAlertCount
}) {
  return (
    <header className="app-header">
      <div className="brand-group">
        <div className="brand-logo-wrap">
          <span className="logo-icon">⛅</span>
          <div className="status-dot-pulse" title="Agent Live & Online"></div>
        </div>
        <div className="brand-text">
          <div className="brand-title">Weather<span className="brand-accent">GPT</span></div>
          <div className="brand-subtitle">AI-Powered Meteorological & Local Alert Assistant</div>
        </div>
      </div>

      <div className="header-controls">
        {/* Language Switcher */}
        <div className="control-box">
          <label htmlFor="langSelect" className="control-label">Language / भाषा</label>
          <select
            id="langSelect"
            className="custom-select"
            value={language}
            onChange={(e) => onLanguageChange(e.target.value)}
          >
            <option value="en">English</option>
            <option value="hi">हिन्दी (Hindi)</option>
            <option value="bn">বাংলা (Bengali)</option>
            <option value="ta">தமிழ் (Tamil)</option>
            <option value="te">తెలుగు (Telugu)</option>
            <option value="mr">मराठी (Marathi)</option>
          </select>
        </div>

        {/* Voice Readout Toggle */}
        <button
          className={`btn-pill ${voiceEnabled ? 'active' : ''}`}
          onClick={onToggleVoice}
          title="Toggle voice readout for rural accessibility"
        >
          <span>{voiceEnabled ? '🔊' : '🔇'}</span>
          <span>{voiceEnabled ? 'Voice ON' : 'Voice OFF'}</span>
        </button>

        {/* LLM Engine Config Button */}
        <button
          className="btn-pill settings-btn"
          onClick={onOpenSettings}
          title="Configure LLM & Multi-Agent Engine"
        >
          <span>⚙️</span>
          <span>LLM: <span className="llm-badge">{llmProvider}</span></span>
        </button>

        {/* Watchdog Status Pill */}
        <div className="watchdog-badge" title="Automated location watchdog monitoring">
          <span className="pulse-indicator"></span>
          <span>Watchdog: {watchdogCount} Active {activeAlertCount > 0 ? `(${activeAlertCount} Alerts)` : ''}</span>
        </div>
      </div>
    </header>
  );
}
