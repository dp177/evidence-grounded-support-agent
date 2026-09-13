import React from 'react';

interface EvidenceScoreProps {
  score: number; // 0.0 - 1.0
}

export const EvidenceScore: React.FC<EvidenceScoreProps> = ({ score }) => {
  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 'var(--space-6)',
        padding: '2px 8px',
        borderRadius: 'var(--radius-xl)',
        backgroundColor: 'var(--pale-blue-wash)',
        border: '1px solid rgba(24, 99, 220, 0.2)',
        fontFamily: 'var(--font-mono)',
        fontSize: '11px',
        color: 'var(--action-blue)',
        fontWeight: 600,
      }}
    >
      <span>SIM:</span>
      <span>{score.toFixed(2)}</span>
    </div>
  );
};
