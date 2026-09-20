import React from 'react';

export default function AgroAdvisoryCard({ advisory }) {
  if (!advisory) return null;

  const isRestricted = !advisory.spray_feasible;

  return (
    <div className="agro-advisory-card">
      <div className="agro-advisory-header">
        <strong>🌾 {advisory.crop} Advisory</strong>
        <span className={`agro-badge ${isRestricted ? 'restricted' : ''}`}>
          {advisory.spray_feasible ? '✓ Safe Spray' : '⚠️ Spray Restricted'}
        </span>
      </div>
      <div style={{ fontSize: '12px', color: '#cbd5e1', marginBottom: '4px' }}>
        <strong>Irrigation:</strong> {advisory.irrigation_details}
      </div>
      <div style={{ fontSize: '11.5px', color: '#94a3b8' }}>
        <strong>Agronomy Tip:</strong> {advisory.crop_tip}
      </div>
    </div>
  );
}
