import React, { useState } from 'react';
import { ClassificationResult } from '../../types/agent';
import { Target, ChevronDown, ChevronUp } from 'lucide-react';

interface InlineClassificationProps {
  classification: ClassificationResult;
}

export const InlineClassification: React.FC<InlineClassificationProps> = ({
  classification,
}) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      style={{
        borderRadius: 'var(--radius-xs)',
        border: '1px solid var(--border-light)',
        backgroundColor: '#ffffff',
        overflow: 'hidden',
        fontSize: '12px',
        margin: 'var(--space-6) 0',
      }}
    >
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '6px 12px',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Target size={12} color="var(--deep-enterprise-green)" />
          <span style={{ color: 'var(--slate)' }}>Understanding ·</span>
          <strong style={{ color: 'var(--ink)' }}>{classification.primary_intent}</strong>
          <span style={{ color: 'var(--muted-slate)' }}>
            ({(classification.confidence * 100).toFixed(0)}% confidence)
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--slate)' }}>
          <span>{expanded ? 'Hide' : 'Details'}</span>
          {expanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
        </div>
      </button>

      {expanded && (
        <div
          style={{
            padding: '10px 14px',
            borderTop: '1px solid var(--border-light)',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            backgroundColor: '#fafafb',
            fontFamily: 'var(--font-mono)',
          }}
        >
          <div>
            <span className="mono-label" style={{ fontSize: '9px' }}>Domain Area</span>
            <div style={{ color: 'var(--ink)', fontSize: '11px', marginTop: '1px' }}>
              {classification.areas.join(' • ')}
            </div>
          </div>

          <div>
            <span className="mono-label" style={{ fontSize: '9px' }}>Conversation States</span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '3px' }}>
              {classification.states.map((st) => (
                <span
                  key={st}
                  style={{
                    padding: '2px 6px',
                    borderRadius: 'var(--radius-xs)',
                    backgroundColor: 'var(--soft-stone)',
                    fontSize: '10px',
                    color: 'var(--ink)',
                  }}
                >
                  ✓ {st}
                </span>
              ))}
            </div>
          </div>

          {classification.intents.length > 1 && (
            <div>
              <span className="mono-label" style={{ fontSize: '9px', color: 'var(--coral)' }}>
                Multi-Intent Detected
              </span>
              <ul style={{ margin: '2px 0 0 14px', padding: 0, fontSize: '11px', color: 'var(--ink)' }}>
                {classification.intents.map((it) => (
                  <li key={it}>{it}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
