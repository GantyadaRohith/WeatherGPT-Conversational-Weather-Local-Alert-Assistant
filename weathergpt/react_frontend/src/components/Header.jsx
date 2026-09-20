import React from 'react';

export default function Header({
  language,
  onLanguageChange,
  voiceEnabled,
  onToggleVoice,
  onOpenSettings,
  onOpenDispatcher,
  onOpenSubscriber,
  llmProvider,
  watchdogCount,
  activeAlertCount,
  dispatchCount = 0,
  dbEngine = 'json_document_store'
}) {
  return (
    <header className="app-header">
      <div className="brand-group">
        <div className="brand-logo-wrap">
          <span className="logo-icon">⛅</span>
          <div className="status-dot-pulse" title="Agent & Watchdog Live"></div>
        </div>
        <div className="brand-text">
          <div className="brand-title">Weather<span className="brand-accent">GPT</span></div>
          <div className="brand-subtitle">AI Meteorological & Scheduled Alert Assistant</div>
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

        {/* Alert Dispatches & Logs Button */}
        <button
          className="btn-pill notif-btn"
          onClick={onOpenDispatcher}
          title="View Alert Dispatches Log & MongoDB Audit"
        >
          <span>📢</span>
          <span>Dispatches <span className="notif-count-badge">{dispatchCount}</span></span>
        </button>

        {/* Subscribe WhatsApp / SMS Button */}
        <button
          className="btn-pill subscribe-btn"
          onClick={onOpenSubscriber}
          title="Subscribe phone for automated WhatsApp / SMS alerts"
        >
          <span>📱</span>
          <span>Subscribe Alerts</span>
        </button>

        {/* System Settings Button */}
        <button
          className="btn-pill settings-btn"
          onClick={onOpenSettings}
          title="Configure LLMs, MongoDB, and Twilio/WhatsApp API"
        >
          <span>⚙️</span>
          <span>
            {llmProvider} · {dbEngine === 'mongodb' ? '🍃 MongoDB' : '💾 JSON DB'}
          </span>
        </button>

        {/* Watchdog Status Pill */}
        <div className="watchdog-badge" title="Automated 60s location watchdog monitoring">
          <span className="pulse-indicator"></span>
          <span>Watchdog: {watchdogCount} Hubs {activeAlertCount > 0 ? `(${activeAlertCount} Alert)` : ''}</span>
        </div>
      </div>
    </header>
  );
}
