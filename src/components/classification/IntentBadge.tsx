import React from 'react';
import { Tag } from 'lucide-react';

interface IntentBadgeProps {
  intent: string;
  isPrimary?: boolean;
}

export const IntentBadge: React.FC<IntentBadgeProps> = ({ intent, isPrimary = false }) => {
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 'var(--space-6)',
        padding: isPrimary ? '4px 12px' : '3px 10px',
        borderRadius: 'var(--radius-xl)',
        backgroundColor: isPrimary ? 'rgba(255, 119, 89, 0.12)' : 'var(--soft-stone)',
        border: `1px solid ${isPrimary ? 'var(--coral)' : 'var(--hairline)'}`,
        color: isPrimary ? '#c2410c' : 'var(--ink)',
        fontFamily: 'var(--font-mono)',
        fontSize: isPrimary ? '12px' : '11px',
        fontWeight: isPrimary ? 600 : 500,
        letterSpacing: '0.2px',
        textTransform: 'uppercase',
      }}
    >
      <Tag size={11} color={isPrimary ? 'var(--coral)' : 'var(--slate)'} />
      {intent}
    </span>
  );
};
