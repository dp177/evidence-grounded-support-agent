import React from 'react';
import { AlertTriangle, ShieldAlert, HelpCircle } from 'lucide-react';

interface ReasonCodeProps {
  code: string;
}

export const ReasonCode: React.FC<ReasonCodeProps> = ({ code }) => {
  const isHighRisk = code.includes('HIGH_RISK') || code.includes('FRAUD') || code.includes('SECURITY');
  const isGrounding = code.includes('GROUNDING');

  const bgColor = isHighRisk
    ? 'rgba(179, 0, 0, 0.08)'
    : isGrounding
    ? 'rgba(255, 119, 89, 0.12)'
    : 'var(--soft-stone)';

  const textColor = isHighRisk
    ? 'var(--error-red)'
    : isGrounding
    ? '#c2410c'
    : 'var(--ink)';

  const borderColor = isHighRisk
    ? 'rgba(179, 0, 0, 0.3)'
    : isGrounding
    ? 'var(--coral)'
    : 'var(--hairline)';

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '3px 9px',
        borderRadius: 'var(--radius-xs)',
        backgroundColor: bgColor,
        color: textColor,
        border: `1px solid ${borderColor}`,
        fontFamily: 'var(--font-mono)',
        fontSize: '11px',
        fontWeight: 600,
      }}
    >
      {isHighRisk ? <ShieldAlert size={12} /> : isGrounding ? <AlertTriangle size={12} /> : <HelpCircle size={12} />}
      {code}
    </span>
  );
};
