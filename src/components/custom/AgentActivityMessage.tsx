import React, { useState } from 'react';
import { AgentActivityStepInfo } from '../../types/customChat';
import { AgentActivityStep } from './AgentActivityStep';
import { Sparkles, ChevronDown, ChevronUp, AlertOctagon, RotateCw } from 'lucide-react';
import { agentApi } from '../../services/agentApi';

interface AgentActivityMessageProps {
  steps: AgentActivityStepInfo[];
  isRunning: boolean;
  isEscalated?: boolean;
  thoughtDuration?: number;
  elapsedSeconds?: number;
  onRetry?: () => void;
  onSwitchToDemo?: () => void;
}

export const AgentActivityMessage: React.FC<AgentActivityMessageProps> = ({
  steps,
  isRunning,
  isEscalated = false,
  thoughtDuration,
  elapsedSeconds,
  onRetry,
  onSwitchToDemo,
}) => {
  const [expanded, setExpanded] = useState(isRunning);
  const isMock = agentApi.isMock();

  // Keep open while running; auto-collapse when completed so the user can read the response
  React.useEffect(() => {
    if (isRunning) {
      setExpanded(true);
    } else {
      setExpanded(false);
    }
  }, [isRunning]);

  if (!steps || steps.length === 0) return null;

  const hasFailed = steps.some((s) => s.status === 'FAILED');
  const failureStep = steps.find((s) => s.status === 'FAILED');
  const activeStep = steps.find((s) => s.status === 'RUNNING');

  const getTitle = () => {
    if (hasFailed) return 'LIVE AGENT UNAVAILABLE';
    if (isRunning) {
      const timeDisplay = elapsedSeconds !== undefined ? ` (${elapsedSeconds.toFixed(1)}s)` : '...';
      return `Thinking${timeDisplay}`;
    }
    if (thoughtDuration !== undefined) {
      return `Thought for ${thoughtDuration}s`;
    }
    if (isEscalated) return 'Agent activity · Human Review Required';
    return 'Agent activity · Completed';
  };

  return (
    <div
      style={{
        borderRadius: 'var(--radius-sm)',
        border: `1px solid ${
          hasFailed
            ? 'rgba(179, 0, 0, 0.3)'
            : isRunning
            ? 'rgba(13, 122, 85, 0.35)'
            : 'var(--card-border)'
        }`,
        backgroundColor: hasFailed ? 'rgba(179, 0, 0, 0.04)' : isRunning ? '#fcfdfd' : '#fafafb',
        boxShadow: isRunning ? '0 2px 10px rgba(13, 122, 85, 0.06)' : 'none',
        overflow: 'hidden',
        fontSize: '13px',
        margin: 'var(--space-8) 0',
        transition: 'all 200ms ease',
      }}
    >
      {/* Animated shimmer progress line while running */}
      {isRunning && <div className="thinking-shimmer-line" />}

      {/* Header / Summary Toggle */}
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '8px 14px',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
          color: 'var(--slate)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          {hasFailed ? (
            <AlertOctagon size={13} color="var(--error-red)" />
          ) : (
            <Sparkles
              size={13}
              color="var(--deep-enterprise-green)"
              className={isRunning ? 'thinking-pulse-icon' : undefined}
            />
          )}
          <span
            style={{
              fontWeight: 600,
              color: hasFailed
                ? 'var(--error-red)'
                : isRunning
                ? 'var(--deep-enterprise-green)'
                : 'var(--ink)',
            }}
          >
            ✦ {getTitle()}
          </span>

          {/* Active step subtitle indicator while running */}
          {isRunning && activeStep && (
            <span
              style={{
                fontSize: '10px',
                color: 'var(--slate)',
                fontWeight: 400,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              · <em>{activeStep.label.replace(/\.\.\.$/, '')}</em>
            </span>
          )}

          {/* Environment Label strictly following requirement 12 */}
          <span
            style={{
              fontSize: '9px',
              padding: '1px 6px',
              borderRadius: '2px',
              backgroundColor: isMock ? 'rgba(0, 0, 0, 0.06)' : 'rgba(13, 122, 85, 0.12)',
              color: isMock ? 'var(--slate)' : 'var(--deep-enterprise-green)',
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            {isRunning && !isMock && <span className="thinking-live-dot" />}
            {isMock ? 'Simulated pipeline activity' : isRunning ? 'Live agent reasoning' : 'Live agent activity'}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span>{expanded ? 'Hide details' : 'View details'}</span>
          {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </div>
      </button>

      {/* Expanded Steps List & Failure Recovery Controls */}
      {expanded && (
        <div
          style={{
            padding: '10px 14px',
            borderTop: '1px solid var(--border-light)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-8)',
            backgroundColor: '#ffffff',
          }}
        >
          {steps.map((step) => (
            <AgentActivityStep key={step.id} step={step} />
          ))}

          {/* Explicit recovery buttons on connection failure */}
          {hasFailed && (
            <div
              style={{
                marginTop: 'var(--space-8)',
                paddingTop: 'var(--space-8)',
                borderTop: '1px solid #fee2e2',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span style={{ fontSize: '11px', color: 'var(--error-red)', fontFamily: 'var(--font-mono)' }}>
                {failureStep?.detail || 'Connection refused'}
              </span>

              <div style={{ display: 'flex', gap: '8px' }}>
                {onRetry && (
                  <button
                    type="button"
                    onClick={onRetry}
                    className="btn-secondary"
                    style={{ fontSize: '11px', padding: '4px 10px', display: 'flex', alignItems: 'center', gap: '4px' }}
                  >
                    <RotateCw size={11} />
                    Retry
                  </button>
                )}

                {onSwitchToDemo && (
                  <button
                    type="button"
                    onClick={onSwitchToDemo}
                    className="btn-primary"
                    style={{ fontSize: '11px', padding: '4px 12px', backgroundColor: 'var(--coral)' }}
                  >
                    Switch to Demo Mode
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
