import React, { useState } from 'react';
import { CustomChatMessage as ICustomChatMessage } from '../../types/customChat';
import { AgentActivityMessage } from './AgentActivityMessage';
import { InlineClassification } from './InlineClassification';
import { InlineEvidence } from './InlineEvidence';
import { InlineGrounding } from './InlineGrounding';
import { HumanHandoffMessage } from './HumanHandoffMessage';
import { Bot, User, Copy, Check, Send, CheckCircle2, Clock } from 'lucide-react';

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
  const [showTiming, setShowTiming] = useState(false);

  const isCustomer = message.role === 'CUSTOMER';
  const resp = message.agentResponse;
  const isEscalated = resp?.escalation.decision === 'HUMAN_REVIEW';
  const isAutoHandle = resp?.escalation.decision === 'AUTO_HANDLE';
  const isGrounded = resp?.grounding.status === 'GROUNDED';
  const canSend = isAutoHandle && isGrounded;

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  // CUSTOMER MESSAGE
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

  // ASSISTANT MESSAGE
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

        {/* 2. Inline Classification summary if available */}
        {resp?.classification && (
          <InlineClassification classification={resp.classification} />
        )}

        {/* 3. Inline Historical Evidence if retrieved */}
        {resp?.retrieved_evidence && resp.retrieved_evidence.length > 0 && (
          <InlineEvidence evidenceList={resp.retrieved_evidence} />
        )}

        {/* 4. Assistant Response Text */}
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

        {/* 5. Inline Grounding Status */}
        {resp?.grounding && (
          <InlineGrounding grounding={resp.grounding} />
        )}

        {/* 6. Human Review / Handoff card if escalated */}
        {isEscalated && resp && (
          <HumanHandoffMessage
            response={resp}
            customerMessage={resp.retrieval_query.customer_query}
            onTakeOver={onTakeOver}
          />
        )}

        {/* 7. Action Bar & Telemetry */}
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
                onClick={() => setShowTiming(!showTiming)}
                className="btn-secondary"
                style={{ padding: '0', fontSize: '11px', color: 'var(--slate)', display: 'flex', alignItems: 'center', gap: '4px' }}
              >
                <Clock size={11} />
                {(resp.trace.total_ms / 1000).toFixed(2)}s timing
              </button>
            )}
          </div>

          <div>
            {canSend && onSendResponse && (
              <button
                type="button"
                onClick={() => onSendResponse(message.text)}
                className="btn-primary"
                style={{ fontSize: '11px', padding: '4px 12px' }}
              >
                <Send size={11} />
                Send to Customer
              </button>
            )}
          </div>
        </div>

        {/* Timing Breakdown Drawer */}
        {showTiming && resp?.trace && (
          <div
            style={{
              padding: '8px 12px',
              backgroundColor: 'var(--soft-stone)',
              borderRadius: 'var(--radius-xs)',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              display: 'flex',
              gap: '12px',
              color: 'var(--ink)',
            }}
          >
            <span>Classify: {resp.trace.classification_ms}ms</span>
            <span>•</span>
            <span>Retrieve: {resp.trace.retrieval_ms}ms</span>
            <span>•</span>
            <span>Rerank: {resp.trace.reranker_ms}ms</span>
            <span>•</span>
            <span>Generate: {resp.trace.generation_ms}ms</span>
            <span>•</span>
            <span>Ground: {resp.trace.grounding_ms}ms</span>
          </div>
        )}
      </div>
    </div>
  );
};
