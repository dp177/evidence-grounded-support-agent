import React, { useState, useEffect, useRef } from 'react';
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
}

// Dedicated micro-component for the live timer:
// Updates its local state every 100ms WITHOUT causing re-renders of the parent message list or activity steps.
const ThinkingTimer: React.FC<{ isRunning: boolean; elapsedSeconds?: number }> = ({ isRunning, elapsedSeconds }) => {
  const [liveElapsed, setLiveElapsed] = useState<number>(0);

  useEffect(() => {
    if (!isRunning) {
      setLiveElapsed(0);
      return;
    }
    const start = Date.now();
    const timer = setInterval(() => {
      setLiveElapsed(Number(((Date.now() - start) / 1000).toFixed(1)));
    }, 100);
    return () => clearInterval(timer);
  }, [isRunning]);

  const displaySec = isRunning ? liveElapsed : (elapsedSeconds ?? 0);
  return <>✦ Thinking ({displaySec.toFixed(1)}s)</>;
};

export const AgentActivityMessage: React.FC<AgentActivityMessageProps> = ({
  steps,
  isRunning,
  isEscalated = false,
  thoughtDuration,
  elapsedSeconds,
  onRetry,
}) => {
  const [expanded, setExpanded] = useState(isRunning);
  const [justCompleted, setJustCompleted] = useState(false);
  const prevRunningRef = useRef(isRunning);
  const isMock = agentApi.isMock();

  // Keep open while running so the user sees real-time progress
  useEffect(() => {
    if (isRunning) {
      setExpanded(true);
    }
  }, [isRunning]);

  // Subtle completion transition pulse when running completes
  useEffect(() => {
    const hasFailed = steps.some((s) => s.status === 'FAILED');
    if (prevRunningRef.current && !isRunning && !hasFailed) {
      setJustCompleted(true);
      const timer = setTimeout(() => setJustCompleted(false), 1200);
      return () => clearTimeout(timer);
    }
    prevRunningRef.current = isRunning;
  }, [isRunning, steps]);

  if (!steps || steps.length === 0) return null;

  const hasFailed = steps.some((s) => s.status === 'FAILED');
  const failureStep = steps.find((s) => s.status === 'FAILED');
  const activeStep = steps.find((s) => s.status === 'RUNNING');

  return (
    <div
      className={justCompleted ? 'agent-activity-panel--just-completed' : undefined}
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
        transition: 'border-color 260ms ease, background-color 260ms ease, box-shadow 260ms ease',
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
          ) : isRunning ? (
            <span className="thinking-indicator-spinner" aria-label="Processing">
              <svg viewBox="0 0 16 16" width="13" height="13" fill="none">
                <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="2" strokeOpacity="0.25" />
                <path d="M14 8a6 6 0 0 0-6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </span>
          ) : (
            <Sparkles size={13} color="var(--deep-enterprise-green)" />
          )}

          <span
            style={{
              fontWeight: 600,
              color: hasFailed
                ? 'var(--error-red)'
                : isRunning
                ? 'var(--deep-enterprise-green)'
                : 'var(--ink)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            {hasFailed ? (
              '✦ LIVE AGENT UNAVAILABLE'
            ) : isRunning ? (
              <ThinkingTimer isRunning={isRunning} elapsedSeconds={elapsedSeconds} />
            ) : thoughtDuration !== undefined ? (
              `✦ Thought for ${thoughtDuration}s`
            ) : isEscalated ? (
              '✦ Agent activity · Human Review Required'
            ) : (
              '✦ Agent activity · Completed'
            )}
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
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
