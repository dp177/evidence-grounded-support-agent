import React, { useState } from 'react';
import { AgentTrace } from '../../types/agent';
import { LatencyBreakdown } from './LatencyBreakdown';
import { Activity, ChevronDown, ChevronUp } from 'lucide-react';

interface TracePanelProps {
  trace?: AgentTrace | null;
}

export const TracePanel: React.FC<TracePanelProps> = ({ trace }) => {
  const [expanded, setExpanded] = useState(false);

  if (!trace) return null;

  return (
    <footer
      style={{
        backgroundColor: '#ffffff',
        borderTop: '1px solid var(--border-light)',
        fontSize: '12px',
        color: 'var(--slate)',
        fontFamily: 'var(--font-mono)',
      }}
    >
      {/* Toggle Bar */}
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: 'var(--space-8) var(--space-24)',
          cursor: 'pointer',
          backgroundColor: '#fafafb',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-12)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)', color: 'var(--ink)' }}>
            <Activity size={13} color="var(--deep-enterprise-green)" />
            <span style={{ fontWeight: 600 }}>PIPELINE OBSERVABILITY TRACE</span>
          </div>
          <span>•</span>
          <span>
            REQ: <strong style={{ color: 'var(--ink)' }}>{trace.request_id}</strong>
          </span>
          <span>•</span>
          <span>
            LATENCY: <strong style={{ color: 'var(--ink)' }}>{(trace.total_ms / 1000).toFixed(2)}s</strong>
          </span>
          <span>•</span>
          <span>
            LLM CALLS: <strong style={{ color: 'var(--ink)' }}>{trace.llm_calls}</strong>
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)', color: 'var(--slate)' }}>
          <span>{expanded ? 'Hide Latency Breakdown' : 'Show Latency Breakdown'}</span>
          {expanded ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
        </div>
      </div>

      {/* Expanded Breakdown */}
      {expanded && (
        <div
          style={{
            padding: 'var(--space-16) var(--space-24)',
            backgroundColor: '#ffffff',
            borderTop: '1px solid var(--card-border)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-12)',
          }}
        >
          <LatencyBreakdown trace={trace} />
        </div>
      )}
    </footer>
  );
};
