import React from 'react';
import { ArrowRight, CheckCircle2, AlertOctagon, RotateCw } from 'lucide-react';

interface RevisionBannerProps {
  revisionCount: number;
  isGrounded: boolean;
}

export const RevisionBanner: React.FC<RevisionBannerProps> = ({
  revisionCount,
  isGrounded,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-8)',
        padding: 'var(--space-8) var(--space-12)',
        backgroundColor: 'var(--soft-stone)',
        borderRadius: 'var(--radius-xs)',
        fontSize: '11px',
        fontFamily: 'var(--font-mono)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--slate)' }}>
        <span>Draft 1</span>
      </div>

      <ArrowRight size={11} color="var(--muted-slate)" />

      {revisionCount > 0 ? (
        <>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              color: 'var(--warning-amber)',
            }}
          >
            <RotateCw size={11} />
            <span>Revision {revisionCount}</span>
          </div>

          <ArrowRight size={11} color="var(--muted-slate)" />

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              color: isGrounded ? 'var(--success-green)' : 'var(--coral)',
              fontWeight: 600,
            }}
          >
            {isGrounded ? (
              <>
                <CheckCircle2 size={12} />
                <span>Passed Grounding</span>
              </>
            ) : (
              <>
                <AlertOctagon size={12} />
                <span>Human Review Triggered</span>
              </>
            )}
          </div>
        </>
      ) : (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            color: 'var(--success-green)',
            fontWeight: 600,
          }}
        >
          <CheckCircle2 size={12} />
          <span>Passed 1st Pass Grounding</span>
        </div>
      )}
    </div>
  );
};
