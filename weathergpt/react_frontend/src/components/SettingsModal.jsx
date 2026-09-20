import React, { useState } from 'react';

export default function SettingsModal({
  isOpen,
  onClose,
  currentProvider,
  onSave
}) {
  const [provider, setProvider] = useState(currentProvider || 'local');
  const [apiKey, setApiKey] = useState('');
  const [savedMessage, setSavedMessage] = useState('');

  if (!isOpen) return null;

  const handleSave = async (e) => {
    e.preventDefault();
    await onSave(provider, apiKey);
    setSavedMessage('Settings applied successfully!');
    setTimeout(() => {
      setSavedMessage('');
      onClose();
    }, 1000);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <div className="modal-header">
          <h3>⚙️ AI Engine & LLM Settings</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSave} className="modal-body">
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
                <small>Llama 3.3 70B Versatile (Ultra-fast LLM tool synthesis)</small>
              </div>

              <div
                className={`provider-card ${provider === 'gemini' ? 'selected' : ''}`}
                onClick={() => setProvider('gemini')}
              >
                <strong>Google Gemini</strong>
                <small>Gemini 1.5 Flash (Multimodal & Indian language reasoning)</small>
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

          {savedMessage && (
            <div style={{ color: '#10b981', fontSize: '13px', fontWeight: 600 }}>
              ✓ {savedMessage}
            </div>
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
      </div>
    </div>
  );
}
