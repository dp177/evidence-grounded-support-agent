import React, { useState } from 'react';
import { ClaimVerification } from '../../types/agent';
import { ClaimStatus } from './ClaimStatus';
import { ChevronDown, ChevronUp, Code2 } from 'lucide-react';

interface ClaimListProps {
  claims: ClaimVerification[];
}

export const ClaimList: React.FC<ClaimListProps> = ({ claims }) => {
  const [showTechnical, setShowTechnical] = useState(false);

  if (claims.length === 0) {
    return (
      <div style={{ fontSize: '12px', color: 'var(--muted-slate)', fontStyle: 'italic' }}>
        No individual propositional claims extracted.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
        {claims.map((claim) => (
          <div
            key={claim.id}
            style={{
              padding: 'var(--space-8) var(--space-10)',
              backgroundColor: '#ffffff',
              border: '1px solid var(--card-border)',
              borderRadius: 'var(--radius-xs)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-4)',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 'var(--space-8)',
              }}
            >
              <ClaimStatus status={claim.status} />
              {claim.supporting_ref && (
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '10px',
                    color: 'var(--muted-slate)',
                  }}
                >
                  Ref: {claim.supporting_ref}
                </span>
              )}
            </div>

            <div style={{ fontSize: '13px', color: 'var(--ink)', lineHeight: '1.4' }}>
              {claim.text}
            </div>
          </div>
        ))}
      </div>

      {/* Expandable Technical Details */}
      <div
        style={{
          borderTop: '1px dashed var(--hairline)',
          paddingTop: 'var(--space-6)',
          marginTop: 'var(--space-4)',
        }}
      >
        <button
          type="button"
          onClick={() => setShowTechnical(!showTechnical)}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-4)',
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            color: 'var(--slate)',
          }}
        >
          <Code2 size={12} />
          <span>Technical Verification Details</span>
          {showTechnical ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </button>

        {showTechnical && (
          <div
            style={{
              marginTop: 'var(--space-6)',
              padding: 'var(--space-8)',
              backgroundColor: 'var(--soft-stone)',
              borderRadius: 'var(--radius-xs)',
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              color: 'var(--ink)',
              lineHeight: '1.5',
            }}
          >
            <div>Algorithm: Grounding Guard V1.1 (NLI entailment matrix)</div>
            <div>Strict Hallucination Threshold: 0.90</div>
            <div>Contradiction Veto: ACTIVE</div>
            <div>Extraneous Claim Filter: STRICT_MODE</div>
          </div>
        )}
      </div>
    </div>
  );
};
