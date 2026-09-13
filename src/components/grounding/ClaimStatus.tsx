import React from 'react';
import { ClaimVerificationStatus } from '../../types/agent';
import { CheckCircle2, AlertTriangle, XCircle, Database, MessageSquare } from 'lucide-react';

interface ClaimStatusProps {
  status: ClaimVerificationStatus;
}

export const ClaimStatus: React.FC<ClaimStatusProps> = ({ status }) => {
  switch (status) {
    case 'CURRENT_CONVERSATION_SUPPORTED':
      return (
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding: '2px 8px',
            borderRadius: 'var(--radius-xs)',
            backgroundColor: 'var(--pale-blue-wash)',
            color: 'var(--action-blue)',
            fontSize: '10px',
            fontFamily: 'var(--font-mono)',
            fontWeight: 600,
          }}
        >
          <MessageSquare size={10} />
          CONVERSATION SUPPORTED
        </span>
      );
    case 'HISTORICAL_EVIDENCE_SUPPORTED':
      return (
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding: '2px 8px',
            borderRadius: 'var(--radius-xs)',
            backgroundColor: 'var(--pale-green-wash)',
            color: 'var(--deep-enterprise-green)',
            fontSize: '10px',
            fontFamily: 'var(--font-mono)',
            fontWeight: 600,
          }}
        >
          <Database size={10} />
          PRECEDENT SUPPORTED
        </span>
      );
    case 'BOTH':
      return (
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding: '2px 8px',
            borderRadius: 'var(--radius-xs)',
            backgroundColor: 'rgba(13, 122, 85, 0.1)',
            color: 'var(--success-green)',
            fontSize: '10px',
            fontFamily: 'var(--font-mono)',
            fontWeight: 600,
          }}
        >
          <CheckCircle2 size={10} />
          FULLY GROUNDED (BOTH)
        </span>
      );
    case 'UNSUPPORTED':
      return (
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding: '2px 8px',
            borderRadius: 'var(--radius-xs)',
            backgroundColor: 'rgba(255, 119, 89, 0.15)',
            color: 'var(--coral)',
            fontSize: '10px',
            fontFamily: 'var(--font-mono)',
            fontWeight: 600,
          }}
        >
          <AlertTriangle size={10} />
          UNSUPPORTED CLAIM
        </span>
      );
    case 'CONTRADICTED':
      return (
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            padding: '2px 8px',
            borderRadius: 'var(--radius-xs)',
            backgroundColor: 'var(--error-tint)',
            color: 'var(--error-red)',
            fontSize: '10px',
            fontFamily: 'var(--font-mono)',
            fontWeight: 600,
          }}
        >
          <XCircle size={10} />
          CONTRADICTED
        </span>
      );
    default:
      return null;
  }
};
