import React, { useState } from 'react';
import { GroundingResult } from '../../types/agent';
import { ChevronDown, ChevronUp, CheckCircle2, AlertTriangle } from 'lucide-react';

interface InlineGroundingProps {
  grounding: GroundingResult;
}

export const InlineGrounding: React.FC<InlineGroundingProps> = ({ grounding }) => {
  const [expanded, setExpanded] = useState(false);
  const isGrounded = grounding.status === 'GROUNDED';
  const isRevised = grounding.revision_count > 0;

  const getHeaderTitle = () => {
    if (!isGrounded) {
      return '⚠ Response needs revision';
    }
    if (isRevised) {
      return `Revised after grounding check · Revision ${grounding.revision_count} · Grounded ✓`;
    }
    return `Grounded ✓ · ${grounding.total_claims} claims checked`;
  };

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
          <span style={{ fontWeight: 600 }}>{getHeaderTitle()}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span>{expanded ? 'Hide verification details' : 'Inspect claims'}</span>
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
            gap: '8px',
            backgroundColor: '#ffffff',
            fontSize: '11px',
            fontFamily: 'var(--font-mono)',
          }}
        >
          {/* Claim Summary Stats Bar */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '4px 8px',
              backgroundColor: '#f8fafc',
              borderRadius: '2px',
              fontSize: '10px',
            }}
          >
            <span>{grounding.total_claims} claims checked</span>
            <span style={{ color: 'var(--deep-enterprise-green)', fontWeight: 600 }}>
              {grounding.supported_claims} supported
            </span>
            <span style={{ color: grounding.unsupported_claims > 0 ? 'var(--coral)' : 'var(--slate)' }}>
              {grounding.unsupported_claims} unsupported
            </span>
            <span style={{ color: grounding.contradicted_claims > 0 ? 'var(--error-red)' : 'var(--slate)' }}>
              {grounding.contradicted_claims} contradicted
            </span>
          </div>

          {/* Individual Claim Breakdown */}
          {grounding.claims.map((claim) => (
            <div
              key={claim.id}
              style={{
                padding: '6px 8px',
                borderRadius: 'var(--radius-xs)',
                backgroundColor: claim.status === 'UNSUPPORTED' ? '#fff1f2' : '#fafafb',
                border: `1px solid ${claim.status === 'UNSUPPORTED' ? '#fecdd3' : 'var(--card-border)'}`,
                display: 'flex',
                flexDirection: 'column',
                gap: '2px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span
                  style={{
                    fontSize: '9px',
                    fontWeight: 600,
                    color:
                      claim.status === 'UNSUPPORTED'
                        ? 'var(--coral)'
                        : claim.status === 'CONTRADICTED'
                        ? 'var(--error-red)'
                        : 'var(--deep-enterprise-green)',
                  }}
                >
                  {claim.status === 'UNSUPPORTED' ? '⚠ UNSUPPORTED CLAIM' : `✓ ${claim.status}`}
                </span>
                <span style={{ fontSize: '9px', color: 'var(--slate)' }}>
                  source: {claim.supporting_ref || claim.source_type}
                </span>
              </div>

              <div style={{ color: 'var(--ink)', fontSize: '11px', lineHeight: '1.4' }}>
                "{claim.text}"
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
