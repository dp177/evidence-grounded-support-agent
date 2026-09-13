import React from 'react';
import { ClassificationResult } from '../../types/agent';
import { IntentBadge } from './IntentBadge';
import { StateBadge } from './StateBadge';
import { ConfidenceMeter } from './ConfidenceMeter';
import { Target, AlertTriangle } from 'lucide-react';

interface ClassificationCardProps {
  classification?: ClassificationResult | null;
}

export const ClassificationCard: React.FC<ClassificationCardProps> = ({
  classification,
}) => {
  if (!classification) {
    return (
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid var(--border-light)',
          borderRadius: 'var(--radius-sm)',
          padding: 'var(--space-20)',
          color: 'var(--muted-slate)',
          fontSize: '13px',
          textAlign: 'center',
        }}
      >
        Awaiting agent execution for intent classification...
      </div>
    );
  }

  const isMultiIntent = classification.intents.length > 1;

  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-sm)',
        padding: 'var(--space-16)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-16)',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--card-border)',
          paddingBottom: 'var(--space-10)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
          <Target size={15} color="var(--deep-enterprise-green)" />
          <h3
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '14px',
              fontWeight: 600,
              color: 'var(--cohere-black)',
            }}
          >
            AI Understanding & Classification
          </h3>
        </div>

        <span className="mono-label" style={{ fontSize: '10px' }}>
          {classification.taxonomy_version || 'TAXONOMY V1'}
        </span>
      </div>

      {/* Primary Intent / Multi-Intent Section */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span className="mono-label" style={{ fontSize: '11px', color: 'var(--slate)' }}>
            {isMultiIntent ? 'MULTI-INTENT DETECTED' : 'PRIMARY INTENT'}
          </span>
          {isMultiIntent && (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '11px',
                color: 'var(--coral)',
                fontFamily: 'var(--font-mono)',
                fontWeight: 600,
              }}
            >
              <AlertTriangle size={12} />
              {classification.intents.length} INTENTS
            </span>
          )}
        </div>

        {isMultiIntent ? (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-6)',
              padding: 'var(--space-8)',
              backgroundColor: 'var(--soft-stone)',
              borderRadius: 'var(--radius-xs)',
              border: '1px solid var(--hairline)',
            }}
          >
            {classification.intents.map((intent, idx) => (
              <div
                key={intent}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-8)',
                  fontSize: '12px',
                  fontFamily: 'var(--font-mono)',
                }}
              >
                <span style={{ fontWeight: 700, color: 'var(--slate)' }}>{idx + 1}.</span>
                <IntentBadge intent={intent} isPrimary={intent === classification.primary_intent} />
              </div>
            ))}
          </div>
        ) : classification.primary_intent ? (
          <div>
            <IntentBadge intent={classification.primary_intent} isPrimary={true} />
          </div>
        ) : (
          <div
            style={{
              padding: '6px 10px',
              backgroundColor: 'var(--soft-stone)',
              borderRadius: 'var(--radius-xs)',
              fontSize: '12px',
              color: 'var(--slate)',
              fontStyle: 'italic',
            }}
          >
            No specific support issue identified yet.
          </div>
        )}
      </div>

      {/* Domain Area */}
      <div>
        <span className="mono-label" style={{ fontSize: '11px', color: 'var(--slate)' }}>
          TAXONOMY DOMAIN AREA
        </span>
        <div
          style={{
            marginTop: 'var(--space-4)',
            fontSize: '13px',
            fontFamily: 'var(--font-mono)',
            color: 'var(--ink)',
            fontWeight: 500,
          }}
        >
          {classification.areas.length > 0 ? classification.areas.join(' • ') : 'None (Ambiguous / Unclassified)'}
        </div>
      </div>

      {/* Confidence Meter */}
      <ConfidenceMeter confidence={classification.confidence} />

      {/* Conversation States */}
      <div>
        <span className="mono-label" style={{ fontSize: '11px', color: 'var(--slate)' }}>
          CONVERSATION STATES
        </span>
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 'var(--space-6)',
            marginTop: 'var(--space-6)',
          }}
        >
          {classification.states.map((st) => (
            <StateBadge key={st} state={st} />
          ))}
        </div>
      </div>
    </div>
  );
};
