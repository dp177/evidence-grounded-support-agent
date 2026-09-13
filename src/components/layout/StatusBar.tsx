import React from 'react';

interface StatusBarProps {
  conversationId: string;
  turnCount: number;
  primaryIntent?: string | null;
  confidence?: number;
  decision?: string;
}

export const StatusBar: React.FC<StatusBarProps> = ({
  conversationId,
  turnCount,
  primaryIntent,
  confidence,
  decision,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '6px var(--space-24)',
        backgroundColor: 'var(--soft-stone)',
        borderBottom: '1px solid var(--border-light)',
        fontSize: '12px',
        color: 'var(--slate)',
        fontFamily: 'var(--font-mono)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-16)' }}>
        <span>
          SESSION:{' '}
          <strong style={{ color: 'var(--ink)' }}>{conversationId}</strong>
        </span>
        <span>•</span>
        <span>
          TURNS: <strong style={{ color: 'var(--ink)' }}>{turnCount}</strong>
        </span>
        {primaryIntent && (
          <>
            <span>•</span>
            <span>
              INTENT:{' '}
              <strong style={{ color: 'var(--ink)' }}>{primaryIntent}</strong>
            </span>
          </>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-16)' }}>
        {confidence !== undefined && (
          <span>
            MODEL CONFIDENCE:{' '}
            <strong style={{ color: 'var(--ink)' }}>
              {(confidence * 100).toFixed(0)}%
            </strong>
          </span>
        )}
        {decision && (
          <>
            <span>•</span>
            <span
              style={{
                color: decision === 'AUTO_HANDLE' ? 'var(--success-green)' : 'var(--warning-amber)',
                fontWeight: 600,
              }}
            >
              {decision === 'AUTO_HANDLE' ? '✓ AUTO-HANDLE' : '⚠ HUMAN REVIEW'}
            </span>
          </>
        )}
      </div>
    </div>
  );
};
