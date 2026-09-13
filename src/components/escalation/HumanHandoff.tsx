import React, { useState } from 'react';
import { AgentResponse, ConversationMessage } from '../../types/agent';
import { UserCheck, Copy, Check, AlertOctagon } from 'lucide-react';

interface HumanHandoffProps {
  response: AgentResponse;
  currentCustomerMessage?: ConversationMessage;
  onTakeOver?: () => void;
}

export const HumanHandoff: React.FC<HumanHandoffProps> = ({
  response,
  currentCustomerMessage,
  onTakeOver,
}) => {
  const [copied, setCopied] = useState(false);

  const escalationSummary =
    response.escalation.summary_for_human ||
    `Customer Issue: ${currentCustomerMessage?.text || 'See conversation'}\n` +
      `Primary Intent: ${response.classification.primary_intent}\n` +
      `Detected States: ${response.classification.states.join(', ')}\n` +
      `Escalation Reasons: ${response.escalation.reason_codes.join(', ')}\n` +
      `Recommended Action: ${response.escalation.action}\n` +
      `Draft Response Prepared: ${response.generated_reply.reply}`;

  const handleCopySummary = () => {
    navigator.clipboard.writeText(escalationSummary);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-12)',
        padding: 'var(--space-16)',
        backgroundColor: '#fffbeb',
        border: '1px solid #fde68a',
        borderRadius: 'var(--radius-sm)',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
          <div
            style={{
              width: '24px',
              height: '24px',
              borderRadius: 'var(--radius-xs)',
              backgroundColor: '#f59e0b',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <AlertOctagon size={15} />
          </div>
          <span
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '13px',
              fontWeight: 700,
              color: '#92400e',
              letterSpacing: '0.3px',
            }}
          >
            HUMAN HANDOFF PACKAGE READY
          </span>
        </div>

        <button
          onClick={handleCopySummary}
          className="btn-secondary"
          style={{
            fontSize: '11px',
            padding: '2px 8px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            color: '#92400e',
          }}
        >
          {copied ? <Check size={12} color="var(--success-green)" /> : <Copy size={12} />}
          {copied ? 'Summary Copied' : 'Copy AI Summary'}
        </button>
      </div>

      {/* Investigation Dossier Brief */}
      <div
        style={{
          padding: 'var(--space-10) var(--space-12)',
          backgroundColor: '#ffffff',
          borderRadius: 'var(--radius-xs)',
          border: '1px solid #fef3c7',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-8)',
          fontSize: '12px',
        }}
      >
        <div>
          <span className="mono-label" style={{ fontSize: '9px' }}>
            AI INVESTIGATION SUMMARY FOR OPERATOR
          </span>
          <div
            style={{
              marginTop: 'var(--space-2)',
              color: 'var(--ink)',
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              lineHeight: '1.4',
              whiteSpace: 'pre-wrap',
            }}
          >
            {escalationSummary}
          </div>
        </div>

        {response.escalation.blocker_reasons.length > 0 && (
          <div>
            <span className="mono-label" style={{ fontSize: '9px', color: 'var(--error-red)' }}>
              AUTOMATION BLOCKERS ENFORCED BY POLICY GATES
            </span>
            <ul
              style={{
                margin: '4px 0 0 var(--space-16)',
                padding: 0,
                color: 'var(--error-red)',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                lineHeight: '1.4',
              }}
            >
              {response.escalation.blocker_reasons.map((b, i) => (
                <li key={i}>{b}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-8)' }}>
        <button
          type="button"
          onClick={onTakeOver}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 18px',
            borderRadius: 'var(--radius-pill)',
            backgroundColor: '#d97706',
            color: '#ffffff',
            border: '1px solid #b45309',
            fontFamily: 'var(--font-body)',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <UserCheck size={15} />
          Take Over Conversation
        </button>
      </div>
    </div>
  );
};
