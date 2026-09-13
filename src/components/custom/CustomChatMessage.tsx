import React, { useState, useEffect, useRef } from 'react';
import { CustomChatMessage as ICustomChatMessage } from '../../types/customChat';
import { AgentActivityMessage } from './AgentActivityMessage';
import { InlineClassification } from './InlineClassification';
import { InlineEvidence } from './InlineEvidence';
import { InlineGrounding } from './InlineGrounding';
import { HumanHandoffMessage } from './HumanHandoffMessage';
import { Bot, Copy, Check, Send, CheckCircle2, ChevronDown, ChevronUp, AlertOctagon, Terminal } from 'lucide-react';

interface CustomChatMessageProps {
  message: ICustomChatMessage;
  turnIndex?: number;
  totalTurns?: number;
  onSendResponse?: (text: string) => void;
  onTakeOver?: () => void;
  onRetry?: () => void;
  onSwitchToDemo?: () => void;
}

export const CustomChatMessage: React.FC<CustomChatMessageProps> = ({
  message,
  turnIndex = 1,
  totalTurns = 1,
  onSendResponse,
  onTakeOver,
  onRetry,
  onSwitchToDemo,
}) => {
  const [copied, setCopied] = useState(false);
  const [showTrace, setShowTrace] = useState(false);
  const [showDebug, setShowDebug] = useState(false);

  // Smooth streaming token / typewriter reveal for assistant responses
  const [displayedText, setDisplayedText] = useState<string>(() => message.text || '');
  const [isStreaming, setIsStreaming] = useState(false);
  const streamRef = useRef<any>(null);

  useEffect(() => {
    if (!message.text) {
      setDisplayedText('');
      setIsStreaming(false);
      return;
    }

    if (displayedText === message.text) {
      return;
    }

    // Stream words smoothly over ~500-800ms
    const fullText = message.text;
    const words = fullText.split(' ');
    let currentWordIdx = 0;
    const chunkSize = Math.max(2, Math.ceil(words.length / 28));
    setIsStreaming(true);

    if (streamRef.current) clearInterval(streamRef.current);
    streamRef.current = setInterval(() => {
      currentWordIdx += chunkSize;
      if (currentWordIdx >= words.length) {
        setDisplayedText(fullText);
        setIsStreaming(false);
        if (streamRef.current) {
          clearInterval(streamRef.current);
          streamRef.current = null;
        }
      } else {
        setDisplayedText(words.slice(0, currentWordIdx).join(' '));
      }
    }, 20);

    return () => {
      if (streamRef.current) {
        clearInterval(streamRef.current);
        streamRef.current = null;
      }
    };
  }, [message.text]);

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
            thoughtDuration={message.thoughtDuration}
            elapsedSeconds={message.elapsedSeconds}
            onRetry={onRetry}
            onSwitchToDemo={onSwitchToDemo}
          />
        )}

        {/* 2. Failure Error Banner */}
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
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600 }}>
              <AlertOctagon size={14} />
              <span>LIVE AGENT UNAVAILABLE</span>
            </div>
            <p style={{ margin: 0, fontSize: '11px', color: '#7f1d1d' }}>
              The live backend pipeline did not respond or returned a connection error. No canned/mock response was fabricated.
            </p>
          </div>
        )}

        {/* 3. Inline Classification summary — shown as soon as classify event arrives */}
        {(resp?.classification || message.partialClassification) && (
          <InlineClassification classification={(resp?.classification || message.partialClassification)!} />
        )}

        {/* 4. Inline Historical Evidence & Reranking — shown as soon as rerank event arrives */}
        {((resp?.retrieved_evidence && resp.retrieved_evidence.length > 0) ||
          (message.partialEvidence && message.partialEvidence.length > 0)) && (
          <InlineEvidence
            evidenceList={(resp?.retrieved_evidence || message.partialEvidence)!}
            reranking={resp?.reranking || message.partialReranking}
            classification={resp?.classification || message.partialClassification}
          />
        )}

        {/* 5. Assistant Response Text — shown as soon as generate event arrives */}
        {(displayedText || message.text || isStreaming) && (
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
              boxShadow: isStreaming ? '0 2px 12px rgba(13, 122, 85, 0.08)' : 'none',
              transition: 'box-shadow 300ms ease',
            }}
          >
            {displayedText || message.text}
            {isStreaming && <span className="typewriter-cursor" />}
          </div>
        )}

        {/* 6. Inline Grounding Status — shown as soon as ground event arrives */}
        {(resp?.grounding || message.partialGrounding) && (
          <InlineGrounding grounding={(resp?.grounding || message.partialGrounding)!} />
        )}

        {/* 7. Inline Decision Status — shown as soon as decide event arrives */}
        {(isAutoHandle || message.partialEscalation?.decision === 'AUTO_HANDLE') && (resp || message.partialEscalation) && (
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
            <span style={{ color: 'var(--ink)', fontWeight: 600 }}>{(resp?.escalation.action || message.partialEscalation?.action)}</span>
          </div>
        )}

        {/* 8. Human Review / Handoff package if escalated */}
        {(isEscalated || message.partialEscalation?.decision === 'HUMAN_REVIEW') && resp && (
          <HumanHandoffMessage
            response={resp}
            customerMessage={resp.retrieval_query.customer_query}
            onTakeOver={onTakeOver}
          />
        )}

        {/* 9. Action Bar, Telemetry & Debug Triggers */}
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

              {resp && (
                <button
                  type="button"
                  onClick={() => setShowDebug(!showDebug)}
                  className="btn-secondary"
                  style={{ padding: '0', fontSize: '11px', color: 'var(--slate)', display: 'flex', alignItems: 'center', gap: '4px' }}
                >
                  <Terminal size={11} />
                  <span>Technical details</span>
                  {showDebug ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
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

        {/* 11. Debug Panel (Requirement 22): LIVE REQUEST & LIVE RESPONSE */}
        {showDebug && resp && (
          <div
            style={{
              padding: '12px 14px',
              backgroundColor: '#17171c',
              color: '#f4f4f5',
              borderRadius: 'var(--radius-xs)',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              display: 'flex',
              flexDirection: 'column',
              gap: '10px',
            }}
          >
            <div>
              <div style={{ color: '#38bdf8', fontWeight: 600, marginBottom: '4px' }}>
                LIVE REQUEST
              </div>
              <div style={{ color: '#a1a1aa' }}>
                POST /api/agent/message
              </div>
              <div style={{ color: '#a1a1aa' }}>
                conversation_id: <span style={{ color: '#ffffff' }}>{resp.conversation_id}</span>
              </div>
              <div style={{ color: '#a1a1aa' }}>
                message_count: <span style={{ color: '#ffffff' }}>{totalTurns}</span>
              </div>
            </div>

            <div style={{ borderTop: '1px solid #27272f', paddingTop: '8px' }}>
              <div style={{ color: '#4ade80', fontWeight: 600, marginBottom: '4px' }}>
                LIVE RESPONSE
              </div>
              <pre
                style={{
                  margin: 0,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  color: '#e4e4e7',
                  maxHeight: '260px',
                  overflowY: 'auto',
                }}
              >
                {JSON.stringify(
                  {
                    conversation_id: resp.conversation_id,
                    classification: resp.classification,
                    retrieval_query: resp.retrieval_query,
                    evidence_count: resp.retrieved_evidence.length,
                    grounding: {
                      status: resp.grounding.status,
                      score: resp.grounding.score,
                      total_claims: resp.grounding.total_claims,
                      supported_claims: resp.grounding.supported_claims,
                      unsupported_claims: resp.grounding.unsupported_claims,
                      revision_count: resp.grounding.revision_count,
                    },
                    escalation: {
                      decision: resp.escalation.decision,
                      action: resp.escalation.action,
                      reason_codes: resp.escalation.reason_codes,
                      blocker_reasons: resp.escalation.blocker_reasons,
                    },
                    trace: resp.trace,
                  },
                  null,
                  2
                )}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
