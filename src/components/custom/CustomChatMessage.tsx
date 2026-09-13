import React, { useState } from 'react';
import { CustomChatMessage as ICustomChatMessage } from '../../types/customChat';
import { AgentActivityMessage } from './AgentActivityMessage';
import { InlineClassification } from './InlineClassification';
import { InlineEvidence } from './InlineEvidence';
import { InlineGrounding } from './InlineGrounding';
import { HumanHandoffMessage } from './HumanHandoffMessage';
import { Bot, Copy, Check, Send, CheckCircle2, ChevronDown, ChevronUp, AlertOctagon } from 'lucide-react';

interface CustomChatMessageProps {
  message: ICustomChatMessage;
  onSendResponse?: (text: string) => void;
  onTakeOver?: () => void;
}

export const CustomChatMessage: React.FC<CustomChatMessageProps> = ({
  message,
  onSendResponse,
  onTakeOver,
}) => {
  const [copied, setCopied] = useState(false);
  const [showTrace, setShowTrace] = useState(false);

  const isCustomer = message.role === 'CUSTOMER';
  const resp = message.agentResponse;
  const isEscalated = resp?.escalation.decision === 'HUMAN_REVIEW';
  const isAutoHandle = resp?.escalation.decision === 'AUTO_HANDLE';
  const isGrounded = resp?.grounding.status === 'GROUNDED';
  const action = resp?.escalation.action;

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  // 1. CUSTOMER MESSAGE BUBBLE
  if (isCustomer) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          margin: 'var(--space-12) 0',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
          <span className="mono-label" style={{ fontSize: '10px' }}>Customer</span>
          <span style={{ fontSize: '10px', color: 'var(--muted-slate)', fontFamily: 'var(--font-mono)' }}>
            {message.timestamp}
          </span>
        </div>

        <div
          style={{
            maxWidth: '75%',
            padding: '12px 18px',
            borderRadius: '18px 18px 4px 18px',
            backgroundColor: 'var(--near-black-primary)',
            color: '#ffffff',
            fontSize: '14px',
            lineHeight: '1.5',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
        >
          {message.text}
        </div>
      </div>
    );
  }

  // 2. ASSISTANT MESSAGE THREAD
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        margin: 'var(--space-16) 0',
        width: '100%',
      }}
    >
      {/* Assistant Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
        <div
          style={{
            width: '22px',
            height: '22px',
            borderRadius: 'var(--radius-xs)',
            backgroundColor: 'var(--deep-enterprise-green)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
          }}
        >
          <Bot size={13} />
        </div>
        <span
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--cohere-black)',
          }}
        >
          AI Support Agent
        </span>
        <span style={{ fontSize: '10px', color: 'var(--muted-slate)', fontFamily: 'var(--font-mono)' }}>
          {message.timestamp}
        </span>
      </div>

      <div
        style={{
          width: '100%',
          maxWidth: '100%',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-8)',
        }}
      >
        {/* 1. Observable Agent Activity Timeline */}
        {message.activitySteps && (
          <AgentActivityMessage
            steps={message.activitySteps}
            isRunning={message.activityStatus === 'RUNNING'}
            isEscalated={isEscalated}
          />
        )}

        {/* 2. Failure Error Message if pipeline threw */}
        {message.activityStatus === 'FAILED' && (
          <div
            style={{
              padding: '12px 16px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              color: 'var(--error-red)',
              fontSize: '12px',
              fontFamily: 'var(--font-mono)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <AlertOctagon size={14} />
            <span>⚠ Agent could not complete the request. Human operator takeover recommended.</span>
          </div>
        )}

        {/* 3. Inline Classification summary */}
        {resp?.classification && (
          <InlineClassification classification={resp.classification} />
        )}

        {/* 4. Inline Historical Evidence & Reranking */}
        {resp?.retrieved_evidence && resp.retrieved_evidence.length > 0 && (
          <InlineEvidence
            evidenceList={resp.retrieved_evidence}
            reranking={resp.reranking}
          />
        )}

        {/* 5. Assistant Response Text */}
        {message.text && (
          <div
            style={{
              padding: '14px 18px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: '#ffffff',
              border: '1px solid var(--border-light)',
              fontSize: '14px',
              lineHeight: '1.6',
              color: 'var(--ink)',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {message.text}
          </div>
        )}

        {/* 6. Inline Grounding Status */}
        {resp?.grounding && (
          <InlineGrounding grounding={resp.grounding} />
        )}

        {/* 7. Inline Decision Status */}
        {isAutoHandle && resp && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              padding: '2px 4px',
            }}
          >
            <CheckCircle2 size={12} color="var(--deep-enterprise-green)" />
            <span style={{ color: 'var(--deep-enterprise-green)', fontWeight: 700 }}>
              AUTO-HANDLE
            </span>
            <span style={{ color: 'var(--slate)' }}>•</span>
            <span style={{ color: 'var(--ink)', fontWeight: 600 }}>{resp.escalation.action}</span>
          </div>
        )}

        {/* 8. Human Review / Handoff package if escalated */}
        {isEscalated && resp && (
          <HumanHandoffMessage
            response={resp}
            customerMessage={resp.retrieval_query.customer_query}
            onTakeOver={onTakeOver}
          />
        )}

        {/* 9. Action Bar & Send Button Safety */}
        {message.text && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '4px 2px',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              color: 'var(--slate)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-12)' }}>
              <button
                type="button"
                onClick={handleCopy}
                className="btn-secondary"
                style={{ padding: '0', fontSize: '11px', color: 'var(--slate)', display: 'flex', alignItems: 'center', gap: '4px' }}
              >
                {copied ? <Check size={11} color="var(--success-green)" /> : <Copy size={11} />}
                {copied ? 'Copied' : 'Copy'}
              </button>

              {resp?.trace && (
                <button
                  type="button"
                  onClick={() => setShowTrace(!showTrace)}
                  className="btn-secondary"
                  style={{ padding: '0', fontSize: '11px', color: 'var(--slate)', display: 'flex', alignItems: 'center', gap: '4px' }}
                >
                  <span>View agent trace</span>
                  {showTrace ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
                </button>
              )}
            </div>

            {/* SEND BUTTON SAFETY: Strictly governed by backend escalation and grounding */}
            <div>
              {isEscalated ? (
                <button
                  type="button"
                  onClick={onTakeOver}
                  className="btn-secondary"
                  style={{
                    fontSize: '11px',
                    padding: '4px 12px',
                    backgroundColor: '#fee2e2',
                    color: '#991b1b',
                    border: '1px solid #f87171',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  TAKE OVER
                </button>
              ) : !isGrounded ? (
                <button
                  type="button"
                  disabled
                  className="btn-secondary"
                  style={{
                    fontSize: '11px',
                    padding: '4px 12px',
                    backgroundColor: '#fff7ed',
                    color: 'var(--coral)',
                    border: '1px solid #fed7aa',
                    fontWeight: 600,
                    cursor: 'not-allowed',
                  }}
                >
                  REVISE
                </button>
              ) : action === 'CLARIFY' ? (
                <button
                  type="button"
                  onClick={() => onSendResponse?.(message.text)}
                  className="btn-primary"
                  style={{ fontSize: '11px', padding: '4px 12px' }}
                >
                  <Send size={11} />
                  SEND CLARIFICATION
                </button>
              ) : isAutoHandle && isGrounded ? (
                <button
                  type="button"
                  onClick={() => onSendResponse?.(message.text)}
                  className="btn-primary"
                  style={{ fontSize: '11px', padding: '4px 12px' }}
                >
                  <Send size={11} />
                  SEND
                </button>
              ) : null}
            </div>
          </div>
        )}

        {/* 10. Trace Details Panel */}
        {showTrace && resp?.trace && (
          <div
            style={{
              padding: '8px 12px',
              backgroundColor: '#f1f5f9',
              borderRadius: 'var(--radius-xs)',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              display: 'flex',
              flexWrap: 'wrap',
              gap: '10px',
              color: 'var(--ink)',
            }}
          >
            <span>Classification: <strong>{resp.trace.classification_ms}ms</strong></span>
            <span>•</span>
            <span>Retrieval: <strong>{resp.trace.retrieval_ms}ms</strong></span>
            <span>•</span>
            <span>Reranking: <strong>{resp.trace.reranker_ms}ms</strong></span>
            <span>•</span>
            <span>Generation: <strong>{resp.trace.generation_ms}ms</strong></span>
            <span>•</span>
            <span>Grounding: <strong>{resp.trace.grounding_ms}ms</strong></span>
            <span>•</span>
            <span style={{ color: 'var(--deep-enterprise-green)', fontWeight: 600 }}>
              Decision (Total: {resp.trace.total_ms}ms)
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
