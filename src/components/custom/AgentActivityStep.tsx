import React, { useState, useEffect, useRef, memo } from 'react';
import { AgentActivityStepInfo } from '../../types/customChat';
import { Check, AlertTriangle, XCircle } from 'lucide-react';

interface AgentActivityStepProps {
  step: AgentActivityStepInfo;
}

export const AgentActivityStep: React.FC<AgentActivityStepProps> = memo(({ step }) => {
  const [displayStatus, setDisplayStatus] = useState<AgentActivityStepInfo['status']>(step.status);
  const [isStoppingSpinner, setIsStoppingSpinner] = useState(false);
  const [isRevealingCheck, setIsRevealingCheck] = useState(false);
  const prevStatusRef = useRef<AgentActivityStepInfo['status']>(step.status);

  useEffect(() => {
    const prev = prevStatusRef.current;
    prevStatusRef.current = step.status;

    // Smooth completion sequence: rotating spinner -> slows/stops -> checkmark reveals
    if (prev === 'RUNNING' && step.status === 'COMPLETED') {
      setIsStoppingSpinner(true);
      const timer1 = setTimeout(() => {
        setIsStoppingSpinner(false);
        setDisplayStatus('COMPLETED');
        setIsRevealingCheck(true);
        const timer2 = setTimeout(() => {
          setIsRevealingCheck(false);
        }, 300);
        return () => clearTimeout(timer2);
      }, 120);
      return () => clearTimeout(timer1);
    } else {
      setDisplayStatus(step.status);
      setIsStoppingSpinner(false);
      setIsRevealingCheck(false);
    }
  }, [step.status]);

  // Determine row CSS modifier
  const getRowClass = () => {
    if (displayStatus === 'RUNNING') return 'agent-stage-row agent-stage-row--active';
    if (displayStatus === 'COMPLETED') return 'agent-stage-row agent-stage-row--complete';
    if (displayStatus === 'WARNING') return 'agent-stage-row agent-stage-row--warning';
    if (displayStatus === 'FAILED') return 'agent-stage-row agent-stage-row--failed';
    return 'agent-stage-row agent-stage-row--pending';
  };

  const renderIcon = () => {
    if (isStoppingSpinner) {
      return (
        <span className="agent-stage-spinner agent-stage-spinner--stopping" aria-label="Finishing">
          <svg viewBox="0 0 16 16" width="13" height="13" fill="none">
            <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="2" strokeOpacity="0.2" />
            <path d="M14 8a6 6 0 0 0-6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </span>
      );
    }

    switch (displayStatus) {
      case 'RUNNING':
        return (
          <span className="agent-stage-spinner agent-stage-spinner--active" aria-label="Running">
            <svg viewBox="0 0 16 16" width="13" height="13" fill="none">
              <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="2" strokeOpacity="0.2" />
              <path d="M14 8a6 6 0 0 0-6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </span>
        );
      case 'COMPLETED':
        return (
          <span
            className={`agent-stage-check ${isRevealingCheck ? 'agent-stage-check--revealing' : ''}`}
            aria-label="Completed"
          >
            <Check size={12} strokeWidth={2.4} />
          </span>
        );
      case 'WARNING':
        return <AlertTriangle size={12} color="var(--warning-amber)" />;
      case 'FAILED':
        return <XCircle size={12} color="var(--error-red)" />;
      default:
        return (
          <span className="agent-stage-pending-icon" aria-label="Pending">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <circle cx="6" cy="6" r="4.5" stroke="currentColor" strokeWidth="1.2" />
            </svg>
          </span>
        );
    }
  };

  return (
    <div className={getRowClass()}>
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
          {renderIcon()}
        </span>
        <span
          style={{
            fontWeight: displayStatus === 'RUNNING' ? 600 : displayStatus === 'COMPLETED' ? 500 : 400,
            transition: 'color 200ms ease, font-weight 200ms ease',
          }}
        >
          {step.label}
        </span>
      </div>

      {step.detail && (
        <span
          style={{
            fontSize: '11px',
            color: displayStatus === 'RUNNING' ? 'var(--deep-enterprise-green)' : 'var(--slate)',
            fontStyle: displayStatus === 'RUNNING' ? 'italic' : 'normal',
            transition: 'color 200ms ease',
          }}
        >
          {step.detail}
        </span>
      )}
    </div>
  );
});

