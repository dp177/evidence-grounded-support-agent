import React, { useState } from 'react';
import { GroundingResult } from '../../types/agent';
import { ShieldCheck, ChevronDown, ChevronUp, CheckCircle2, AlertTriangle } from 'lucide-react';

interface InlineGroundingProps {
  grounding: GroundingResult;
}

export const InlineGrounding: React.FC<InlineGroundingProps> = ({ grounding }) => {
  const [expanded, setExpanded] = useState(false);
  const isGrounded = grounding.status === 'GROUNDED';

  return (
    <div
      style={{
        borderRadius: 'var(--radius-xs)',
        border: `1px solid ${isGrounded ? 'rgba(13, 122, 85, 0.2)' : 'rgba(255, 119, 89, 0.3)'}`,
        backgroundColor: isGrounded ? 'var(--pale-green-wash)' : 'rgba(255, 119, 89, 0.08)',
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
          color: isGrounded ? 'var(--deep-enterprise-green)' : 'var(--coral)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {isGrounded ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
          <span style={{ fontWeight: 600 }}>
            {isGrounded
              ? `Grounding Verified (${grounding.supported_claims}/${grounding.total_claims} claims supported)`
              : 'Grounding Verification Warning'}
          </span>
          {grounding.revision_count > 0 && (
            <span
              style={{
                backgroundColor: 'rgba(0, 0, 0, 0.06)',
                padding: '1px 5px',
                borderRadius: '2px',
                fontSize: '10px',
              }}
            >
              revised ({grounding.revision_count})
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span>{expanded ? 'Hide claims' : 'View claims'}</span>
          {expanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
        </div>
      </button>

      {expanded && (
        <div
          style={{
            padding: '10px 14px',
            borderTop: '1px solid rgba(0, 0, 0, 0.08)',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px',
            backgroundColor: '#ffffff',
            fontSize: '11px',
          }}
        >
          {grounding.claims.map((claim) => (
            <div
              key={claim.id}
              style={{
                padding: '6px 8px',
                borderRadius: 'var(--radius-xs)',
                backgroundColor: '#fafafb',
                border: '1px solid var(--card-border)',
                display: 'flex',
                flexDirection: 'column',
                gap: '2px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '9px',
                    fontWeight: 600,
                    color:
                      claim.status === 'UNSUPPORTED'
                        ? 'var(--coral)'
                        : 'var(--deep-enterprise-green)',
                  }}
                >
                  {claim.status}
                </span>
                {claim.supporting_ref && (
                  <span style={{ color: 'var(--muted-slate)', fontSize: '9px' }}>
                    Ref: {claim.supporting_ref}
                  </span>
                )}
              </div>
              <div style={{ color: 'var(--ink)' }}>{claim.text}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
