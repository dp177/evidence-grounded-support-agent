import React, { useState } from 'react';
import { AgentActivityStepInfo } from '../../types/customChat';
import { AgentActivityStep } from './AgentActivityStep';
import { Sparkles, ChevronDown, ChevronUp, AlertOctagon } from 'lucide-react';
import { agentApi } from '../../services/agentApi';

interface AgentActivityMessageProps {
  steps: AgentActivityStepInfo[];
  isRunning: boolean;
  isEscalated?: boolean;
}

export const AgentActivityMessage: React.FC<AgentActivityMessageProps> = ({
  steps,
  isRunning,
  isEscalated = false,
}) => {
  const [expanded, setExpanded] = useState(isRunning);
  const isMock = agentApi.isMock();

  // Auto-collapse when finished, keep open when running
  React.useEffect(() => {
    if (isRunning) {
      setExpanded(true);
    }
  }, [isRunning]);

  if (!steps || steps.length === 0) return null;

  const hasFailed = steps.some((s) => s.status === 'FAILED');

  const getTitle = () => {
    if (hasFailed) return 'Agent activity · Execution Issue';
    if (isRunning) return 'Agent activity · In progress';
    if (isEscalated) return 'Agent activity · Human Review Required';
    return 'Agent activity · Completed';
  };

  return (
    <div
      style={{
        borderRadius: 'var(--radius-sm)',
        border: `1px solid ${hasFailed ? 'rgba(179, 0, 0, 0.3)' : 'var(--card-border)'}`,
        backgroundColor: hasFailed ? 'rgba(179, 0, 0, 0.04)' : '#fafafb',
        overflow: 'hidden',
        fontSize: '13px',
        margin: 'var(--space-8) 0',
      }}
    >
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {hasFailed ? (
            <AlertOctagon size={13} color="var(--error-red)" />
          ) : (
            <Sparkles size={12} color="var(--deep-enterprise-green)" />
          )}
          <span style={{ fontWeight: 600, color: hasFailed ? 'var(--error-red)' : 'var(--ink)' }}>
            ✦ {getTitle()}
          </span>

          {isMock && (
            <span
              style={{
                fontSize: '9px',
                padding: '1px 5px',
                borderRadius: '2px',
                backgroundColor: 'rgba(0, 0, 0, 0.06)',
                color: 'var(--slate)',
              }}
            >
              Simulated pipeline activity
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span>{expanded ? 'Hide steps' : 'View steps'}</span>
          {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </div>
      </button>

      {/* Expanded Steps List */}
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
        </div>
      )}
    </div>
  );
};
