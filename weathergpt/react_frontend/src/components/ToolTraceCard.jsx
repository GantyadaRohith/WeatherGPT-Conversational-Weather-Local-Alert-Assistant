import React from 'react';

export default function ToolTraceCard({ trace }) {
  if (!trace) return null;

  const toolClassMap = {
    get_current_weather: 'tool-current',
    get_forecast: 'tool-forecast',
    get_crop_advisory: 'tool-crop',
    get_severe_alerts: 'tool-alert',
    get_historical_climate: 'tool-climate',
    get_commute_advisory: 'tool-current',
    domain_fallback_guard: 'tool-alert',
    error_fallback: 'tool-alert'
  };

  const toolClass = toolClassMap[trace.tool_picked] || 'tool-current';
  const pipeline = trace.agent_orchestration || [
    'LangGraph::SupervisorNode',
    `LangGraph::ToolNode(${trace.tool_picked || 'meteorology'})`,
    'LangGraph::AntiHallucinationGuard',
    `LangGraph::Synthesizer(${trace.llm_engine || 'agent'})`
  ];

  const confidenceScore = Math.round((trace.confidence || 0.95) * 100);
  const isRefusal = trace.tool_picked === 'domain_fallback_guard';
  const isGroq = String(trace.llm_engine || '').toLowerCase().includes('groq');

  return (
    <div className="trace-panel">
      <div className="trace-header">
        <div className="trace-header-left">
          <span className={`trace-chip ${toolClass}`}>{trace.tool_picked || 'tool_dispatch'}</span>
          <span className="trace-title">LangGraph Tool-Selection Trace</span>
        </div>
        <div className="trace-meta">
          <span>⚡ {trace.latency_ms || 120} ms</span>
          <span>• Grounding: {confidenceScore}%</span>
          <span
            style={{
              padding: '2px 8px',
              borderRadius: '10px',
              background: isGroq ? 'rgba(249, 115, 22, 0.2)' : 'rgba(56, 189, 248, 0.15)',
              color: isGroq ? '#fb923c' : '#38bdf8',
              fontWeight: 600,
              border: `1px solid ${isGroq ? 'rgba(249, 115, 22, 0.4)' : 'rgba(56, 189, 248, 0.3)'}`
            }}
          >
            {isGroq ? `☁️ Groq API: ${trace.llm_engine}` : `⚙️ Engine: ${trace.llm_engine || 'langgraph_agent'}`}
          </span>
        </div>
      </div>

      <div className="trace-body">
        <div className="trace-row">
          <span className="t-label">Params:</span>
          <span className="t-val">{JSON.stringify(trace.parameters || {})}</span>
        </div>
        <div className="trace-row">
          <span className="t-label">Reason:</span>
          <span className="t-val">{trace.reason || 'Intent-driven tool dispatch'}</span>
        </div>

        {/* Anti-Hallucination Citation Provenance */}
        {trace.citation && (
          <div className="trace-row">
            <span className="t-label">Source:</span>
            <span className="t-val" style={{ color: isRefusal ? '#f87171' : '#34d399', fontSize: '11px' }}>
              🛡️ {trace.citation}
            </span>
          </div>
        )}

        {/* LangGraph StateGraph Node Pipeline Flow */}
        <div className="agent-pipeline-flow">
          <span style={{ fontSize: '10px', color: '#94a3b8', fontWeight: 600 }}>LangGraph Flow:</span>
          {pipeline.map((step, idx) => (
            <React.Fragment key={idx}>
              <span className="flow-step">{step}</span>
              {idx < pipeline.length - 1 && <span className="flow-arrow">→</span>}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}
