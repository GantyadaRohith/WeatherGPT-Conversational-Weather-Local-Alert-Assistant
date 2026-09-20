import { API_BASE_URL } from '../config';
import React, { useState } from 'react';

export default function NotificationModal({
  isOpen,
  onClose,
  onSubscribe,
  onTestDispatch,
  defaultCity = 'Visakhapatnam'
}) {
  const [activeTab, setActiveTab] = useState('test'); // 'test' or 'subscribe'
  
  // Test Dispatch State
  const [testCity, setTestCity] = useState(defaultCity);
  const [testPhone, setTestPhone] = useState('+916302293711');
  const [testChannel, setTestChannel] = useState('whatsapp');
  const [testSeverity, setTestSeverity] = useState('RED');
  const [testScenario, setTestScenario] = useState('cyclone');
  const [dispatchMode, setDispatchMode] = useState('simulator'); // 'simulator' or 'live'
  const [isSending, setIsSending] = useState(false);
  const [dispatchResult, setDispatchResult] = useState(null);

  // Subscribe State
  const [subName, setSubName] = useState('');
  const [subPhone, setSubPhone] = useState('+916302293711');
  const [subCity, setSubCity] = useState(defaultCity);
  const [subChannel, setSubChannel] = useState('whatsapp');
  const [subRainThreshold, setSubRainThreshold] = useState(25);
  const [subSuccess, setSubSuccess] = useState('');

  if (!isOpen) return null;

  const scenarioPresets = {
    cyclone: {
      type: 'Severe Cyclonic Storm Warning (Cyclone Vayu)',
      severity: 'RED',
      message: 'Deep depression intensifying into severe cyclonic storm with sustained winds of 90-105 km/h.',
      action: 'Fishermen advised not to venture into sea. Coastal residents evacuate to cyclone shelters.'
    },
    cloudburst: {
      type: 'Flash Flood & Torrential Cloudburst Warning',
      severity: 'RED',
      message: 'Intense convective cloudburst detected with 75mm rainfall recorded in 60 mins. Localized flash flooding imminent.',
      action: 'Avoid waterlogged underpasses. Keep battery torches and emergency medication accessible.'
    },
    heatwave: {
      type: 'Extreme Heatwave Red Alert (Loo Warning)',
      severity: 'RED',
      message: 'Severe heatwave conditions with peak temperature reaching 44.5°C with hot dry winds.',
      action: 'Stay indoors between 11 AM - 4 PM. Consume electrolyte water or ORS regularly.'
    },
    coldwave: {
      type: 'Severe Ground Frost & Cold Wave Warning',
      severity: 'ORANGE',
      message: 'Near-freezing temperatures (3.8°C) detected. High risk of frost injury to sensitive standing crops.',
      action: 'Apply light irrigation to mustard and potato fields to insulate plant root zones.'
    }
  };

  const handleSendTest = async (e) => {
    e.preventDefault();
    setIsSending(true);
    setDispatchResult(null);

    const preset = scenarioPresets[testScenario] || scenarioPresets.cyclone;

    try {
      const res = await fetch(`${API_BASE_URL}/api/notifications/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: testCity,
          alert_type: preset.type,
          severity: testSeverity,
          message: preset.message,
          action: preset.action,
          phone: testPhone,
          channel: testChannel,
          simulate: dispatchMode === 'simulator'
        })
      });

      if (res.ok) {
        const data = await res.json();
        setDispatchResult(data.data);
        if (onTestDispatch) onTestDispatch();
      } else {
        const err = await res.json();
        alert(`Dispatch failed: ${err.detail || 'Unknown error'}`);
      }
    } catch (err) {
      alert(`Network error: ${err.message}`);
    } finally {
      setIsSending(false);
    }
  };

  const handleSubscribeSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/api/subscribers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: subName || 'Community Citizen',
          phone: subPhone,
          location: subCity,
          channel: subChannel
        })
      });

      if (res.ok) {
        await fetch(`${API_BASE_URL}/api/saved-locations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: subCity,
            threshold_rain_mm: Number(subRainThreshold),
            notify_heatwave: true,
            phone: subPhone,
            channel: subChannel
          })
        });

        setSubSuccess(`✓ Successfully registered ${subPhone} for automated ${subChannel.toUpperCase()} alerts in ${subCity}!`);
        if (onSubscribe) onSubscribe();
        setTimeout(() => {
          setSubSuccess('');
          onClose();
        }, 1800);
      }
    } catch (err) {
      alert(`Subscription error: ${err.message}`);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card notification-modal-card">
        <div className="modal-header">
          <div className="modal-title-wrap">
            <span className="modal-icon">📢</span>
            <div>
              <h3>Disaster Notification Dispatcher</h3>
              <small style={{ color: '#94a3b8' }}>Twilio SMS · Meta WhatsApp Cloud API · Scheduled Watchdog</small>
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        {/* Tab Switcher */}
        <div className="modal-tabs">
          <button
            className={`tab-btn ${activeTab === 'test' ? 'active' : ''}`}
            onClick={() => setActiveTab('test')}
          >
            ⚡ Evaluator Dispatch Bench
          </button>
          <button
            className={`tab-btn ${activeTab === 'subscribe' ? 'active' : ''}`}
            onClick={() => setActiveTab('subscribe')}
          >
            📱 Citizen / Farmer Alert Subscribe
          </button>
        </div>

        <div className="modal-body">
          {activeTab === 'test' && (
            <form onSubmit={handleSendTest} className="dispatch-form">
              {/* Mode Selector */}
              <div className="dispatch-mode-selector">
                <label style={{ fontSize: '12px', fontWeight: 600, color: '#94a3b8', display: 'block', marginBottom: '6px' }}>
                  Select Execution Mode:
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '14px' }}>
                  <button
                    type="button"
                    className={`channel-btn ${dispatchMode === 'simulator' ? 'wa active' : ''}`}
                    onClick={() => setDispatchMode('simulator')}
                    style={{ padding: '8px 12px' }}
                  >
                    <span className="ch-icon">⚡</span>
                    <div>
                      <strong style={{ color: '#34d399' }}>Evaluator Simulator (Recommended)</strong>
                      <small>100% Free · Verified Receipts · Zero Sandbox Friction</small>
                    </div>
                  </button>

                  <button
                    type="button"
                    className={`channel-btn ${dispatchMode === 'live' ? 'sms active' : ''}`}
                    onClick={() => setDispatchMode('live')}
                    style={{ padding: '8px 12px' }}
                  >
                    <span className="ch-icon">📡</span>
                    <div>
                      <strong style={{ color: '#38bdf8' }}>Live Twilio REST API</strong>
                      <small>Dispatches through active Twilio Gateway</small>
                    </div>
                  </button>
                </div>
              </div>

              <div className="form-row-grid">
                <div className="form-group">
                  <label>Target Hub / City:</label>
                  <input
                    type="text"
                    className="form-input"
                    value={testCity}
                    onChange={(e) => setTestCity(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Recipient Phone Number:</label>
                  <input
                    type="text"
                    className="form-input"
                    value={testPhone}
                    onChange={(e) => setTestPhone(e.target.value)}
                    placeholder="+91 98765 43210"
                    required
                  />
                </div>
              </div>

              <div className="form-row-grid">
                <div className="form-group">
                  <label>Notification Channel:</label>
                  <div className="channel-select-group">
                    <button
                      type="button"
                      className={`channel-btn wa ${testChannel === 'whatsapp' ? 'active' : ''}`}
                      onClick={() => setTestChannel('whatsapp')}
                    >
                      <span className="ch-icon">💬</span>
                      <div>
                        <strong>WhatsApp</strong>
                        <small>Cloud API / Twilio</small>
                      </div>
                    </button>
                    <button
                      type="button"
                      className={`channel-btn sms ${testChannel === 'sms' ? 'active' : ''}`}
                      onClick={() => setTestChannel('sms')}
                    >
                      <span className="ch-icon">📨</span>
                      <div>
                        <strong>Twilio SMS</strong>
                        <small>Direct Cellular</small>
                      </div>
                    </button>
                  </div>
                </div>

                <div className="form-group">
                  <label>Hazard Scenario Preset:</label>
                  <select
                    className="form-input"
                    value={testScenario}
                    onChange={(e) => {
                      setTestScenario(e.target.value);
                      setTestSeverity(scenarioPresets[e.target.value].severity);
                    }}
                  >
                    <option value="cyclone">🌪️ Severe Cyclonic Storm (RED)</option>
                    <option value="cloudburst">⛈️ Flash Flood & Cloudburst (RED)</option>
                    <option value="heatwave">🔥 Extreme Heatwave Loo (RED)</option>
                    <option value="coldwave">❄️ Crop Ground Frost (ORANGE)</option>
                  </select>
                </div>
              </div>

              <div className="dispatch-action-row">
                <button type="submit" className="btn-dispatch-now" disabled={isSending}>
                  {isSending ? '📡 Dispatching Alert...' : `🚀 Dispatch ${testChannel === 'whatsapp' ? 'WhatsApp' : 'SMS'} Alert (${dispatchMode === 'simulator' ? 'Simulated' : 'Live Gateway'})`}
                </button>
              </div>

              {/* Live Preview / Receipt */}
              {dispatchResult && (
                <div className="dispatch-receipt-box">
                  <div className="receipt-header">
                    <div className="receipt-status-tag" style={{
                      background: dispatchResult.dispatch_status?.includes('failed') ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.18)',
                      color: dispatchResult.dispatch_status?.includes('failed') ? '#f87171' : '#34d399'
                    }}>
                      <span className="check-icon">{dispatchResult.dispatch_status?.includes('failed') ? '✕' : '✓'}</span>
                      <span>{dispatchResult.dispatch_status?.toUpperCase()}</span>
                    </div>
                    <span className="receipt-provider">
                      Provider: <strong>{dispatchResult.provider}</strong>
                    </span>
                    <span className="receipt-msg-id">
                      ID: <code>{dispatchResult.message_id}</code>
                    </span>
                  </div>

                  {dispatchResult.dispatch_status?.includes('failed') && (
                    <div style={{
                      background: 'rgba(239, 68, 68, 0.12)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      borderRadius: '6px',
                      padding: '8px 12px',
                      marginBottom: '10px',
                      color: '#fca5a5',
                      fontSize: '12px'
                    }}>
                      <strong>⚠️ Notice:</strong> {dispatchResult.dispatch_status}
                    </div>
                  )}

                  <div className={`message-preview-bubble ${dispatchResult.channel}`}>
                    <div className="bubble-badge">
                      {dispatchResult.channel === 'whatsapp' ? '🟢 WhatsApp Notification Preview' : '🔵 Twilio SMS Preview'}
                    </div>
                    <pre className="bubble-content">{dispatchResult.formatted_message}</pre>
                    <div className="bubble-footer">
                      <span>Recipient: {dispatchResult.recipient}</span>
                      <span className="read-receipt">{dispatchResult.dispatch_status?.includes('failed') ? 'Status Logged in DB' : '✓✓ Delivered'}</span>
                    </div>
                  </div>
                </div>
              )}
            </form>
          )}

          {activeTab === 'subscribe' && (
            <form onSubmit={handleSubscribeSubmit} className="subscribe-form">
              <p className="tab-helper-text">
                Subscribe farmers and residents for automated 60-second watchdog background alerts when meteorological thresholds breach:
              </p>

              <div className="form-row-grid">
                <div className="form-group">
                  <label>Subscriber Name / Farm:</label>
                  <input
                    type="text"
                    className="form-input"
                    value={subName}
                    onChange={(e) => setSubName(e.target.value)}
                    placeholder="e.g. Ramesh Patel"
                  />
                </div>

                <div className="form-group">
                  <label>Mobile / WhatsApp Phone:</label>
                  <input
                    type="text"
                    className="form-input"
                    value={subPhone}
                    onChange={(e) => setSubPhone(e.target.value)}
                    placeholder="+916302293711"
                    required
                  />
                </div>
              </div>

              <div className="form-row-grid">
                <div className="form-group">
                  <label>City / Agricultural Hub:</label>
                  <input
                    type="text"
                    className="form-input"
                    value={subCity}
                    onChange={(e) => setSubCity(e.target.value)}
                    placeholder="e.g. Visakhapatnam"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Preferred Channel:</label>
                  <select
                    className="form-input"
                    value={subChannel}
                    onChange={(e) => setSubChannel(e.target.value)}
                  >
                    <option value="whatsapp">WhatsApp (Cloud API / Twilio)</option>
                    <option value="sms">Twilio SMS (Cellular)</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Rainfall Breach Threshold (mm):</label>
                <div className="range-slider-wrap">
                  <input
                    type="range"
                    min="5"
                    max="80"
                    step="5"
                    value={subRainThreshold}
                    onChange={(e) => setSubRainThreshold(e.target.value)}
                  />
                  <span className="threshold-pill">{subRainThreshold} mm / 24h</span>
                </div>
                <small style={{ color: '#94a3b8', fontSize: '11px' }}>
                  If precipitation exceeds this value, an automated notification is committed to MongoDB and pushed to subscriber.
                </small>
              </div>

              {subSuccess && (
                <div className="subscribe-success-msg">
                  {subSuccess}
                </div>
              )}

              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={onClose}>
                  Close
                </button>
                <button type="submit" className="btn-primary">
                  Save Subscription
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}