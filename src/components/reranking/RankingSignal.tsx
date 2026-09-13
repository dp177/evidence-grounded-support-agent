import React from 'react';
import { RerankingSignal as IRerankingSignal } from '../../types/agent';

interface RankingSignalProps {
  signal: IRerankingSignal;
}

export const RankingSignal: React.FC<RankingSignalProps> = ({ signal }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '12px',
        }}
      >
        <span style={{ color: 'var(--ink)', fontWeight: 500 }}>{signal.label}</span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--slate)' }}>
          {signal.score}%
        </span>
      </div>

      <div
        style={{
          height: '5px',
          width: '100%',
          backgroundColor: 'var(--card-border)',
          borderRadius: 'var(--radius-full)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${signal.score}%`,
            backgroundColor: 'var(--near-black-primary)',
            borderRadius: 'var(--radius-full)',
          }}
        />
      </div>
    </div>
  );
};
