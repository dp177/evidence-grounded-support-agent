import React from 'react';
import { AgentActivityStepInfo } from '../../types/customChat';
import { Check, Loader2, AlertTriangle, XCircle, Circle } from 'lucide-react';

interface AgentActivityStepProps {
  step: AgentActivityStepInfo;
}

export const AgentActivityStep: React.FC<AgentActivityStepProps> = ({ step }) => {
  const getIcon = () => {
    switch (step.status) {
      case 'COMPLETED':
        return <Check size={12} color="var(--deep-enterprise-green)" />;
      case 'RUNNING':
        return <Loader2 size={12} className="spin-animation" color="var(--action-blue)" />;
      case 'WARNING':
        return <AlertTriangle size={12} color="var(--warning-amber)" />;
      case 'FAILED':
        return <XCircle size={12} color="var(--error-red)" />;
      default:
        return <Circle size={8} color="var(--muted-slate)" />;
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '12px',
        color: step.status === 'IDLE' ? 'var(--muted-slate)' : 'var(--ink)',
        fontFamily: 'var(--font-mono)',
        padding: step.status === 'RUNNING' ? '4px 8px' : '2px 8px',
        backgroundColor: step.status === 'RUNNING' ? 'rgba(13, 122, 85, 0.06)' : 'transparent',
        borderRadius: 'var(--radius-xs)',
        transition: 'all 200ms ease',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
        <span
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '16px',
            height: '16px',
            flexShrink: 0,
          }}
        >
          {getIcon()}
        </span>
        <span
          style={{
            fontWeight: step.status === 'RUNNING' ? 600 : step.status === 'COMPLETED' ? 500 : 400,
            color: step.status === 'RUNNING' ? 'var(--deep-enterprise-green)' : undefined,
          }}
        >
          {step.label}
        </span>
      </div>

      {step.detail && (
        <span
          style={{
            fontSize: '11px',
            color: step.status === 'RUNNING' ? 'var(--deep-enterprise-green)' : 'var(--slate)',
            fontStyle: step.status === 'RUNNING' ? 'italic' : 'normal',
          }}
        >
          {step.detail}
        </span>
      )}
    </div>
  );
};
