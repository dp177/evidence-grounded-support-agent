import React, { useState } from 'react';
import { AgentResponse, ConversationMessage } from '../../types/agent';
import { AlertOctagon, UserCheck, Copy, Check, ChevronDown, ChevronUp } from 'lucide-react';

interface HumanHandoffMessageProps {
  response: AgentResponse;
  customerMessage: string;
  onTakeOver?: () => void;
}

export const HumanHandoffMessage: React.FC<HumanHandoffMessageProps> = ({
  response,
  customerMessage,
  onTakeOver,
}) => {
  const [copied, setCopied] = useState(false);
  const [showPackage, setShowPackage] = useState(false);

  const isHighRisk = response.escalation.reason_codes.some((c) =>
    c.includes('HIGH_RISK') || c.includes('SECURITY') || c.includes('FRAUD')
  );

  const summary =
    response.escalation.summary_for_human ||
    `Customer Statement: "${customerMessage}"\n` +
      `Detected Intent: ${response.classification.primary_intent}\n` +
      `Escalation Reasons: ${response.escalation.reason_codes.join(', ')}\n` +
      `Policy Blocker: ${response.escalation.blocker_reasons.join('; ') || 'Human review required'}\n` +
      `Prepared AI Draft: "${response.generated_reply.reply}"`;

  const handleCopy = () => {
    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div
      style={{
        borderRadius: 'var(--radius-sm)',
        border: `1px solid ${isHighRisk ? 'rgba(179, 0, 0, 0.3)' : '#fdba74'}`,
        backgroundColor: isHighRisk ? 'var(--error-tint)' : '#fff7ed',
        padding: 'var(--space-14)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-10)',
        marginTop: 'var(--space-8)',
      }}
    >
      {/* Alert Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertOctagon size={16} color={isHighRisk ? 'var(--error-red)' : '#ea580c'} />
          <span
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '13px',
              fontWeight: 700,
              color: isHighRisk ? 'var(--error-red)' : '#9a3412',
              letterSpacing: '0.2px',
            }}
          >
            HUMAN REVIEW REQUIRED
          </span>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
          {response.escalation.reason_codes.map((rc) => (
            <span
              key={rc}
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '10px',
                fontWeight: 600,
                padding: '2px 6px',
                borderRadius: 'var(--radius-xs)',
                backgroundColor: isHighRisk ? 'rgba(179, 0, 0, 0.12)' : 'rgba(234, 88, 12, 0.12)',
                color: isHighRisk ? 'var(--error-red)' : '#c2410c',
              }}
            >
              {rc}
            </span>
          ))}
        </div>
      </div>

      <p style={{ fontSize: '13px', color: 'var(--ink)', lineHeight: '1.4' }}>
        {isHighRisk
          ? 'Automation halted: High-risk security or fraud indicators detected. This case has been locked for a human agent.'
          : 'Automation halted: Policy gates flagged classification ambiguity or low support confidence. A human operator must review or clarify.'}
      </p>

      {/* Expandable Hand-off Package */}
      <div
        style={{
          borderTop: '1px solid rgba(0, 0, 0, 0.08)',
          paddingTop: 'var(--space-6)',
        }}
      >
        <button
          type="button"
          onClick={() => setShowPackage(!showPackage)}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            color: 'var(--slate)',
          }}
        >
          <span>{showPackage ? 'Hide Handoff Dossier' : 'Inspect AI Handoff Summary'}</span>
          {showPackage ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </button>

        {showPackage && (
          <div
            style={{
              marginTop: 'var(--space-6)',
              padding: '10px',
              backgroundColor: '#ffffff',
              borderRadius: 'var(--radius-xs)',
              border: '1px solid var(--border-light)',
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              color: 'var(--ink)',
              whiteSpace: 'pre-wrap',
              lineHeight: '1.5',
            }}
          >
            {summary}
          </div>
        )}
      </div>

      {/* Buttons */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingTop: 'var(--space-4)',
        }}
      >
        <button
          type="button"
          onClick={handleCopy}
          className="btn-secondary"
          style={{ padding: '0', fontSize: '11px', color: 'var(--slate)' }}
        >
          {copied ? <Check size={12} color="var(--success-green)" /> : <Copy size={12} />}
          {copied ? 'Summary Copied' : 'Copy AI Summary'}
        </button>

        <button
          type="button"
          onClick={onTakeOver}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 14px',
            borderRadius: 'var(--radius-pill)',
            backgroundColor: isHighRisk ? 'var(--error-red)' : '#ea580c',
            color: '#ffffff',
            border: 'none',
            fontFamily: 'var(--font-body)',
            fontSize: '12px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <UserCheck size={13} />
          Take Over Conversation
        </button>
      </div>
    </div>
  );
};
