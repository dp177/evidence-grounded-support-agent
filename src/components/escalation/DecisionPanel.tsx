import React from 'react';
import { AgentResponse, ConversationMessage } from '../../types/agent';
import { ReasonCode } from './ReasonCode';
import { HumanHandoff } from './HumanHandoff';
import { AlertOctagon, ShieldAlert, Check } from 'lucide-react';

interface DecisionPanelProps {
  response?: AgentResponse | null;
  currentCustomerMessage?: ConversationMessage;
  onTakeOver?: () => void;
}

export const DecisionPanel: React.FC<DecisionPanelProps> = ({
  response,
  currentCustomerMessage,
  onTakeOver,
}) => {
  if (!response) {
    return (
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid var(--border-light)',
          borderRadius: 'var(--radius-sm)',
          padding: 'var(--space-20)',
          color: 'var(--muted-slate)',
          fontSize: '13px',
          textAlign: 'center',
        }}
      >
        Awaiting agent execution for policy escalation decision...
      </div>
    );
  }

  const { escalation } = response;
  const isAutoHandle = escalation.decision === 'AUTO_HANDLE';
  const isHighRisk = escalation.reason_codes.some(
    (c) => c.includes('HIGH_RISK') || c.includes('SECURITY') || c.includes('FRAUD')
  );

  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-sm)',
        padding: 'var(--space-16)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-12)',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--card-border)',
          paddingBottom: 'var(--space-8)',
        }}
      >
        <h3
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--cohere-black)',
          }}
        >
          Safety & Escalation Policy Decision
        </h3>

        <span className="mono-label" style={{ fontSize: '10px' }}>
          DETERMINISTIC GATE
        </span>
      </div>

      {/* STATE A: AUTO-HANDLE */}
      {isAutoHandle ? (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-10)',
            padding: 'var(--space-14)',
            backgroundColor: 'var(--pale-green-wash)',
            border: '1px solid rgba(13, 122, 85, 0.25)',
            borderRadius: 'var(--radius-xs)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
            <div
              style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: 'var(--deep-enterprise-green)',
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Check size={15} />
            </div>
            <div>
              <span
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '14px',
                  fontWeight: 700,
                  color: 'var(--deep-enterprise-green)',
                }}
              >
                Safe to handle automatically
              </span>
              <div style={{ fontSize: '12px', color: '#166534', marginTop: '1px' }}>
                All safety, classification, retrieval, and grounding gates passed without exception.
              </div>
            </div>
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              paddingTop: 'var(--space-8)',
              borderTop: '1px solid rgba(13, 122, 85, 0.15)',
              fontSize: '12px',
              fontFamily: 'var(--font-mono)',
            }}
          >
            <span>
              Action:{' '}
              <strong style={{ color: 'var(--deep-enterprise-green)' }}>
                {escalation.action}
              </strong>
            </span>
            <div style={{ display: 'flex', gap: 'var(--space-6)' }}>
              {escalation.reason_codes.map((c) => (
                <ReasonCode key={c} code={c} />
              ))}
            </div>
          </div>
        </div>
      ) : (
        /* STATE B: HUMAN REVIEW */
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-12)',
            padding: 'var(--space-14)',
            backgroundColor: isHighRisk ? 'var(--error-tint)' : '#fff7ed',
            border: `1px solid ${isHighRisk ? 'rgba(179, 0, 0, 0.25)' : '#fdba74'}`,
            borderRadius: 'var(--radius-xs)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
            <div
              style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: isHighRisk ? 'var(--error-red)' : '#ea580c',
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {isHighRisk ? <ShieldAlert size={15} /> : <AlertOctagon size={15} />}
            </div>
            <div>
              <span
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '14px',
                  fontWeight: 700,
                  color: isHighRisk ? 'var(--error-red)' : '#9a3412',
                }}
              >
                Human Review Required
              </span>
              <div
                style={{
                  fontSize: '12px',
                  color: isHighRisk ? '#991b1b' : '#c2410c',
                  marginTop: '1px',
                }}
              >
                {isHighRisk
                  ? 'CRITICAL SAFETY BLOCK: High-risk security or fraud concern halts automation.'
                  : 'Policy gate prevented auto-dispatch; human confirmation required.'}
              </div>
            </div>
          </div>

          <div>
            <span className="mono-label" style={{ fontSize: '10px' }}>
              ESCALATION REASON CODES
            </span>
            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 'var(--space-6)',
                marginTop: 'var(--space-4)',
              }}
            >
              {escalation.reason_codes.map((c) => (
                <ReasonCode key={c} code={c} />
              ))}
            </div>
          </div>

          {/* Full Human Hand-off Dossier */}
          <HumanHandoff
            response={response}
            currentCustomerMessage={currentCustomerMessage}
            onTakeOver={onTakeOver}
          />
        </div>
      )}
    </div>
  );
};
