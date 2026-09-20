import React from 'react';

export default function HazardAlertBanner({ alert, onDismiss }) {
  if (!alert) return null;

  return (
    <div className="hazard-banner">
      <div className="hazard-content">
        <span className="hazard-icon">🚨</span>
        <div className="hazard-info">
          <strong>{alert.type || 'Extreme Hazard Warning'}</strong>
          <p>{alert.message || 'Severe meteorological conditions detected in active region.'}</p>
        </div>
      </div>
      <button className="hazard-dismiss" onClick={onDismiss}>✕</button>
    </div>
  );
}
