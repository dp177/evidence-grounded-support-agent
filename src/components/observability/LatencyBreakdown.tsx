import React from 'react';
import { AgentTrace } from '../../types/agent';

interface LatencyBreakdownProps {
  trace: AgentTrace;
}

export const LatencyBreakdown: React.FC<LatencyBreakdownProps> = ({ trace }) => {
  const total = trace.total_ms || 1;
  const pctClassify = (trace.classification_ms / total) * 100;
  const pctRetrieval = (trace.retrieval_ms / total) * 100;
  const pctRerank = (trace.reranker_ms / total) * 100;
  const pctGen = (trace.generation_ms / total) * 100;
  const pctGround = (trace.grounding_ms / total) * 100;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
      {/* Visual proportional timing bar */}
      <div
        style={{
          height: '8px',
          width: '100%',
          backgroundColor: 'var(--soft-stone)',
          borderRadius: 'var(--radius-full)',
          overflow: 'hidden',
          display: 'flex',
        }}
      >
        <div
          title={`Classification: ${trace.classification_ms}ms`}
          style={{ width: `${pctClassify}%`, backgroundColor: '#3b82f6' }}
        />
        <div
          title={`Retrieval: ${trace.retrieval_ms}ms`}
          style={{ width: `${pctRetrieval}%`, backgroundColor: '#10b981' }}
        />
        <div
          title={`Reranking: ${trace.reranker_ms}ms`}
          style={{ width: `${pctRerank}%`, backgroundColor: '#8b5cf6' }}
        />
        <div
          title={`Generation: ${trace.generation_ms}ms`}
          style={{ width: `${pctGen}%`, backgroundColor: '#f59e0b' }}
        />
        <div
          title={`Grounding: ${trace.grounding_ms}ms`}
          style={{ width: `${pctGround}%`, backgroundColor: '#003c33' }}
        />
      </div>

      {/* Latency table */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(6, 1fr)',
          gap: 'var(--space-8)',
          fontSize: '11px',
          fontFamily: 'var(--font-mono)',
          textAlign: 'center',
        }}
      >
        <div>
          <span style={{ color: '#3b82f6' }}>● CLASSIFY</span>
          <div style={{ fontWeight: 600, color: 'var(--ink)' }}>{trace.classification_ms} ms</div>
        </div>
        <div>
          <span style={{ color: '#10b981' }}>● RETRIEVE</span>
          <div style={{ fontWeight: 600, color: 'var(--ink)' }}>{trace.retrieval_ms} ms</div>
        </div>
        <div>
          <span style={{ color: '#8b5cf6' }}>● RERANK</span>
          <div style={{ fontWeight: 600, color: 'var(--ink)' }}>{trace.reranker_ms} ms</div>
        </div>
        <div>
          <span style={{ color: '#f59e0b' }}>● GENERATE</span>
          <div style={{ fontWeight: 600, color: 'var(--ink)' }}>{trace.generation_ms} ms</div>
        </div>
        <div>
          <span style={{ color: '#003c33' }}>● GROUND</span>
          <div style={{ fontWeight: 600, color: 'var(--ink)' }}>{trace.grounding_ms} ms</div>
        </div>
        <div>
          <span style={{ color: 'var(--slate)' }}>TOTAL E2E</span>
          <div style={{ fontWeight: 700, color: 'var(--ink)' }}>
            {(trace.total_ms / 1000).toFixed(2)} s
          </div>
        </div>
      </div>
    </div>
  );
};
