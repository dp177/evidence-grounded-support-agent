import React from 'react';

interface ConfidenceMeterProps {
  confidence: number; // 0.0 - 1.0
}

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({ confidence }) => {
  const percentage = Math.round(confidence * 100);
  const isHigh = percentage >= 80;
  const isMedium = percentage >= 60 && percentage < 80;

  const barColor = isHigh
    ? 'var(--deep-enterprise-green)'
    : isMedium
    ? 'var(--action-blue)'
    : 'var(--warning-amber)';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <span
          className="mono-label"
          style={{ fontSize: '11px', color: 'var(--slate)', fontWeight: 600 }}
        >
          MODEL CONFIDENCE
        </span>
        <span
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '12px',
            fontWeight: 700,
            color: barColor,
          }}
        >
          {percentage}%
        </span>
      </div>

      <div
        style={{
          height: '6px',
          width: '100%',
          backgroundColor: 'var(--card-border)',
          borderRadius: 'var(--radius-full)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${percentage}%`,
            backgroundColor: barColor,
            borderRadius: 'var(--radius-full)',
            transition: 'width 0.4s ease-out',
          }}
        />
      </div>

      <span
        style={{
          fontSize: '10px',
          color: 'var(--muted-slate)',
          fontFamily: 'var(--font-mono)',
        }}
      >
        Uncalibrated classifier softmax estimate
      </span>
    </div>
  );
};
