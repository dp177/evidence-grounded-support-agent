import React from 'react';
import { Layers, Info, CheckCircle } from 'lucide-react';
import { ClassificationResult } from '../../types/agent';

interface ConversationStateCardProps {
  classification?: ClassificationResult | null;
  turnCount: number;
}

export const ConversationStateCard: React.FC<ConversationStateCardProps> = ({
  classification,
  turnCount,
}) => {
  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-sm)',
        padding: 'var(--space-16)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-12)',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--card-border)',
          paddingBottom: 'var(--space-8)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
          <Layers size={14} color="var(--deep-enterprise-green)" />
          <span
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '13px',
              fontWeight: 600,
              color: 'var(--cohere-black)',
            }}
          >
            Live Conversation State
          </span>
        </div>

        <span
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            color: 'var(--muted-slate)',
          }}
        >
          {turnCount} TURNS LOGGED
        </span>
      </div>

      {/* State details */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-12)' }}>
        <div>
          <span className="mono-label" style={{ fontSize: '10px' }}>
            Current Intent
          </span>
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              fontWeight: 600,
              color: classification?.primary_intent ? 'var(--ink)' : 'var(--muted-slate)',
              marginTop: 'var(--space-2)',
            }}
          >
            {classification?.primary_intent || 'AWAITING RUN'}
          </div>
        </div>

        <div>
          <span className="mono-label" style={{ fontSize: '10px' }}>
            Model Confidence
          </span>
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              fontWeight: 600,
              color: classification ? 'var(--deep-enterprise-green)' : 'var(--muted-slate)',
              marginTop: 'var(--space-2)',
            }}
          >
            {classification ? `${(classification.confidence * 100).toFixed(0)}%` : '—'}
          </div>
        </div>
      </div>

      {/* Active Detected States */}
      <div>
        <span className="mono-label" style={{ fontSize: '10px' }}>
          Current States (Multi-Turn)
        </span>
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 'var(--space-6)',
            marginTop: 'var(--space-6)',
          }}
        >
          {classification?.states && classification.states.length > 0 ? (
            classification.states.map((st) => (
              <span
                key={st}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '3px 8px',
                  borderRadius: 'var(--radius-xs)',
                  backgroundColor: 'var(--soft-stone)',
                  border: '1px solid var(--hairline)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  color: 'var(--ink)',
                  fontWeight: 500,
                }}
              >
                <CheckCircle size={10} color="var(--deep-enterprise-green)" />
                {st}
              </span>
            ))
          ) : (
            <span
              style={{
                fontSize: '12px',
                color: 'var(--muted-slate)',
                fontStyle: 'italic',
              }}
            >
              No state detected yet.
            </span>
          )}
        </div>
      </div>

      {/* Critical System Boundary Disclaimer */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: 'var(--space-6)',
          padding: 'var(--space-8) var(--space-10)',
          borderRadius: 'var(--radius-xs)',
          backgroundColor: '#fafafb',
          border: '1px solid var(--border-light)',
          fontSize: '11px',
          color: 'var(--slate)',
          lineHeight: '1.4',
        }}
      >
        <Info size={13} color="var(--muted-slate)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <span>
          <strong>Boundary Notice:</strong> State is derived solely from the active conversation timeline (Live Context ≠ Historical Knowledge).
        </span>
      </div>
    </div>
  );
};
