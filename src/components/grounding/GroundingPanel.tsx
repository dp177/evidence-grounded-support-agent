import React from 'react';
import { GroundingResult } from '../../types/agent';
import { ClaimList } from './ClaimList';
import { RevisionBanner } from './RevisionBanner';
import { ShieldCheck, AlertTriangle, XCircle, CheckCircle2 } from 'lucide-react';

interface GroundingPanelProps {
  grounding?: GroundingResult | null;
}

export const GroundingPanel: React.FC<GroundingPanelProps> = ({ grounding }) => {
  if (!grounding) {
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
        Awaiting agent execution for grounding verification...
      </div>
    );
  }

  const isGrounded = grounding.status === 'GROUNDED';
  const isRequiresRevision = grounding.status === 'REQUIRES_REVISION';

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
          <ShieldCheck size={15} color="var(--deep-enterprise-green)" />
          <h3
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '13px',
              fontWeight: 600,
              color: 'var(--cohere-black)',
            }}
          >
            Grounding & Verification
          </h3>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
          {isGrounded ? (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                color: 'var(--success-green)',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                fontWeight: 600,
              }}
            >
              <CheckCircle2 size={13} />
              SCORE: {grounding.score.toFixed(2)}
            </span>
          ) : isRequiresRevision ? (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                color: 'var(--warning-amber)',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                fontWeight: 600,
              }}
            >
              <AlertTriangle size={13} />
              REVISION REQUIRED
            </span>
          ) : (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                color: 'var(--coral)',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                fontWeight: 600,
              }}
            >
              <XCircle size={13} />
              GROUNDING FAILED
            </span>
          )}
        </div>
      </div>

      {/* Metrics Row */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 'var(--space-8)',
          backgroundColor: '#fafafb',
          borderRadius: 'var(--radius-xs)',
          padding: 'var(--space-8) var(--space-12)',
          border: '1px solid var(--card-border)',
          textAlign: 'center',
        }}
      >
        <div>
          <div className="mono-label" style={{ fontSize: '9px' }}>
            TOTAL
          </div>
          <div style={{ fontSize: '13px', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
            {grounding.total_claims}
          </div>
        </div>
        <div>
          <div className="mono-label" style={{ fontSize: '9px', color: 'var(--success-green)' }}>
            SUPPORTED
          </div>
          <div
            style={{
              fontSize: '13px',
              fontWeight: 600,
              fontFamily: 'var(--font-mono)',
              color: 'var(--success-green)',
            }}
          >
            {grounding.supported_claims}
          </div>
        </div>
        <div>
          <div className="mono-label" style={{ fontSize: '9px', color: 'var(--coral)' }}>
            UNSUPPORTED
          </div>
          <div
            style={{
              fontSize: '13px',
              fontWeight: 600,
              fontFamily: 'var(--font-mono)',
              color: grounding.unsupported_claims > 0 ? 'var(--coral)' : 'var(--slate)',
            }}
          >
            {grounding.unsupported_claims}
          </div>
        </div>
        <div>
          <div className="mono-label" style={{ fontSize: '9px', color: 'var(--error-red)' }}>
            CONTRADICTED
          </div>
          <div
            style={{
              fontSize: '13px',
              fontWeight: 600,
              fontFamily: 'var(--font-mono)',
              color: grounding.contradicted_claims > 0 ? 'var(--error-red)' : 'var(--slate)',
            }}
          >
            {grounding.contradicted_claims}
          </div>
        </div>
      </div>

      {/* Revision Loop Stepper */}
      <RevisionBanner
        revisionCount={grounding.revision_count}
        isGrounded={isGrounded}
      />

      {/* Unsupported Claims Alert if any */}
      {grounding.unsupported_claim_details && grounding.unsupported_claim_details.length > 0 && (
        <div
          style={{
            padding: 'var(--space-8) var(--space-10)',
            borderRadius: 'var(--radius-xs)',
            backgroundColor: 'rgba(255, 119, 89, 0.1)',
            border: '1px solid rgba(255, 119, 89, 0.3)',
            fontSize: '11px',
            color: '#c2410c',
          }}
        >
          {grounding.unsupported_claim_details.map((detail, i) => (
            <div key={i}>{detail}</div>
          ))}
        </div>
      )}

      {/* Claim-Level Breakdown List */}
      <div>
        <span className="mono-label" style={{ fontSize: '10px' }}>
          PROPOSITIONAL CLAIM VERIFICATIONS
        </span>
        <div style={{ marginTop: 'var(--space-6)' }}>
          <ClaimList claims={grounding.claims} />
        </div>
      </div>
    </div>
  );
};
