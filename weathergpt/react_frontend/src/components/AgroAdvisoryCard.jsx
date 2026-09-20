import React from 'react';

export default function AgroAdvisoryCard({ advisory }) {
  if (!advisory) return null;

  const isRestricted = !advisory.spray_feasible;
  const ranked = advisory.ranked_crops || [];

  return (
    <div className="agro-advisory-card">
      <div className="agro-advisory-header">
        <strong>🌾 {advisory.is_best_recommendation ? 'Crop Suitability Ranking (AI Agronomy)' : `${advisory.crop} Advisory`}</strong>
        <span className={`agro-badge ${isRestricted ? 'restricted' : ''}`}>
          {advisory.spray_feasible ? '✓ Safe Spray' : '⚠️ Spray Restricted'}
        </span>
      </div>

      {ranked.length > 0 && (
        <div className="agro-ranked-section" style={{ marginTop: '8px', marginBottom: '8px' }}>
          <div style={{ fontSize: '11px', color: '#38bdf8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
            Top Recommended Crops (Best Match for Current Soil & Weather):
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {ranked.slice(0, 4).map((rc, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  background: 'rgba(255, 255, 255, 0.04)',
                  padding: '6px 10px',
                  borderRadius: '8px',
                  border: '1px solid rgba(255, 255, 255, 0.08)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '11px', fontWeight: 700, color: '#38bdf8' }}>#{idx + 1}</span>
                  <strong style={{ fontSize: '12.5px', color: '#f8fafc' }}>{rc.crop_name}</strong>
                  <span style={{ fontSize: '11px', color: '#94a3b8' }}>({rc.ideal_temp})</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: '12px',
                      background: rc.score >= 85 ? 'rgba(34, 197, 94, 0.18)' : 'rgba(56, 189, 248, 0.18)',
                      color: rc.score >= 85 ? '#4ade80' : '#38bdf8',
                      border: `1px solid ${rc.score >= 85 ? 'rgba(34, 197, 94, 0.3)' : 'rgba(56, 189, 248, 0.3)'}`
                    }}
                  >
                    {rc.score}% Match ({rc.badge})
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ fontSize: '12px', color: '#cbd5e1', marginTop: '6px', marginBottom: '4px' }}>
        <strong>Irrigation:</strong> {advisory.irrigation_details}
      </div>
      <div style={{ fontSize: '11.5px', color: '#94a3b8' }}>
        <strong>Agronomy Tip:</strong> {advisory.crop_tip}
      </div>
    </div>
  );
}

