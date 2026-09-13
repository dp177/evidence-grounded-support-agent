import React from 'react';
import { CheckCircle2 } from 'lucide-react';

interface StateBadgeProps {
  state: string;
}

export const StateBadge: React.FC<StateBadgeProps> = ({ state }) => {
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '3px 9px',
        borderRadius: 'var(--radius-xs)',
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-light)',
        color: 'var(--ink)',
        fontFamily: 'var(--font-mono)',
        fontSize: '11px',
        fontWeight: 500,
      }}
    >
      <CheckCircle2 size={11} color="var(--deep-enterprise-green)" />
      {state}
    </span>
  );
};
