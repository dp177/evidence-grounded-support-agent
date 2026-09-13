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
      {/* Primary compact summary conforming to example layout */}
      <div
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '6px 12px',
          background: 'none',
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
          flexWrap: 'wrap',
          gap: '8px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <Target size={12} color="var(--deep-enterprise-green)" />
          <span style={{ color: 'var(--slate)', fontWeight: 600 }}>Understanding:</span>
          
          {/* Primary Intent / Ambiguous status */}
          {classification.status === 'AMBIGUOUS' || !classification.primary_intent ? (
            <span
              style={{
                color: 'var(--slate)',
                fontStyle: 'italic',
                fontSize: '11px',
              }}
            >
              No specific support issue identified yet.
            </span>
          ) : (
            <span
              style={{
                backgroundColor: 'var(--coral)',
                color: '#ffffff',
                padding: '1px 6px',
                borderRadius: '2px',
                fontSize: '10px',
                fontWeight: 700,
              }}
            >
              {classification.primary_intent}
            </span>
          )}

          {/* States */}
          {classification.states.map((st) => (
            <span
              key={st}
              style={{
                padding: '1px 5px',
                borderRadius: '2px',
                backgroundColor: 'var(--soft-stone)',
                color: 'var(--ink)',
                fontSize: '10px',
              }}
            >
              {st}
            </span>
          ))}

          {/* Model Confidence */}
          <span style={{ color: 'var(--slate)', fontSize: '10px', marginLeft: '4px' }}>
            MODEL CONFIDENCE <strong>{classification.confidence.toFixed(2)}</strong>
          </span>
        </div>

        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            color: 'var(--slate)',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            fontFamily: 'var(--font-mono)',
            fontSize: '10px',
            padding: 0,
          }}
        >
          <span>{expanded ? 'Hide taxonomy' : 'More'}</span>
          {expanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
        </button>
      </div>

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
              {classification.areas.length > 0 ? classification.areas.join(' • ') : 'None (Ambiguous / Unclassified)'}
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
