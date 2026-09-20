import { API_BASE_URL } from '../config';
import React, { useState, useEffect } from 'react';

export default function DispatchHistoryDrawer({
  isOpen,
  onClose,
  onOpenDispatcher
}) {
  const [dispatches, setDispatches] = useState([]);
  const [dbStatus, setDbStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [triggering, setTriggering] = useState(false);

  const fetchDispatches = async () => {
    setLoading(true);
    try {
      const [dispRes, dbRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/notifications/dispatches?limit=25`),
        fetch(`${API_BASE_URL}/api/database/status`)
      ]);

      if (dispRes.ok) {
        const data = await dispRes.json();
        setDispatches(data.dispatches || []);
      }
      if (dbRes.ok) {
        const data = await dbRes.json();
        setDbStatus(data);
      }
    } catch (err) {
      console.warn('Dispatch fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerWatchdogDispatch = async () => {
    setTriggering(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/alerts/watchdog-dispatch`, { method: 'POST' });
      if (res.ok) {
        await fetchDispatches();
      }
    } catch (err) {
      console.warn('Trigger error:', err);
    } finally {
      setTriggering(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchDispatches();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-card drawer-card">
        <div className="modal-header">
          <div className="modal-title-wrap">
            <span className="modal-icon">📜</span>
            <div>
              <h3>Disaster Alert Audit & Dispatch Log</h3>
              <small style={{ color: '#94a3b8' }}>
                MongoDB Persistent Document Store · Track A · A2
              </small>
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        {/* Database Status Strip */}
        <div className="db-telemetry-strip">
          <div className="db-info-pill">
            <span className="pill-dot green"></span>
            <span>Database: <strong>{dbStatus?.engine === 'mongodb' ? 'MongoDB Atlas / Instance' : 'Persistent Document Store'}</strong></span>
          </div>

          <div className="db-counts-group">
            <span className="count-tag">
              💾 <strong>{dbStatus?.counts?.alert_dispatches || dispatches.length}</strong> Dispatches Logged
            </span>
            <span className="count-tag">
              📍 <strong>{dbStatus?.counts?.saved_locations || 0}</strong> Monitored Hubs
            </span>
            <span className="count-tag">
              👥 <strong>{dbStatus?.counts?.subscribers || 0}</strong> Subscribers
            </span>
          </div>
        </div>

        {/* Action Controls */}
        <div className="drawer-actions-bar">
          <button
            className="btn-sm btn-primary"
            onClick={onOpenDispatcher}
          >
            ⚡ Test New Dispatch
          </button>

          <button
            className="btn-sm btn-secondary"
            onClick={handleTriggerWatchdogDispatch}
            disabled={triggering}
          >
            {triggering ? 'Evaluating Watchdog...' : '🔄 Run Watchdog Evaluation Now'}
          </button>

          <button
            className="btn-sm btn-ghost"
            onClick={fetchDispatches}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : '↻ Refresh Log'}
          </button>
        </div>

        {/* Dispatches Feed */}
        <div className="dispatches-feed">
          {dispatches.length === 0 ? (
            <div className="empty-dispatches">
              <div className="empty-icon">📭</div>
              <h4>No Alert Dispatches Yet</h4>
              <p>Click "Test New Dispatch" or run the automated watchdog to trigger hazard warnings.</p>
            </div>
          ) : (
            dispatches.map((item, idx) => (
              <div key={item._id || idx} className="dispatch-log-item">
                <div className="dispatch-item-top">
                  <div className="dispatch-badges">
                    <span className={`chan-badge ${item.channel}`}>
                      {item.channel === 'whatsapp' ? '🟢 WhatsApp' : '🔵 Twilio SMS'}
                    </span>
                    <span className={`sev-badge ${item.severity?.toLowerCase()}`}>
                      {item.severity}
                    </span>
                    <span className="city-badge">
                      📍 {item.location}
                    </span>
                  </div>
                  <div className="dispatch-timestamp">
                    {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </div>
                </div>

                <div className="dispatch-hazard-title">
                  <strong>{item.type}</strong>
                </div>

                <div className="dispatch-msg-body">
                  {item.message}
                </div>

                {item.action && (
                  <div className="dispatch-action-directive">
                    🛡️ <strong>Safety Directive:</strong> {item.action}
                  </div>
                )}

                <div className="dispatch-item-bottom">
                  <span className="dispatch-recipient">
                    To: <code>{item.recipient}</code>
                  </span>
                  <span className="dispatch-receipt">
                    Status: <span className="status-highlight">✓ {item.status}</span> ({item.provider})
                  </span>
                  <span className="dispatch-id">
                    ID: <code>{item.message_id}</code>
                  </span>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
