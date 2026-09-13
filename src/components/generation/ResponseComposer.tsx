import React, { useState, useEffect } from 'react';
import { GeneratedResponse, EscalationDecision } from '../../types/agent';
import { EvidenceReference } from './EvidenceReference';
import { ResponseActions } from './ResponseActions';
import { Sparkles, History, CheckCheck, AlertCircle } from 'lucide-react';

interface ResponseComposerProps {
  generatedReply?: GeneratedResponse | null;
  decision?: EscalationDecision;
  onSendResponse: (replyText: string) => void;
  onRegenerate: () => void;
  onTakeOver?: () => void;
  onSelectEvidence?: (docId: string) => void;
  isRunning?: boolean;
}

export const ResponseComposer: React.FC<ResponseComposerProps> = ({
  generatedReply,
  decision,
  onSendResponse,
  onRegenerate,
  onTakeOver,
  onSelectEvidence,
  isRunning = false,
}) => {
  const [text, setText] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (generatedReply?.reply) {
      setText(generatedReply.reply);
    }
  }, [generatedReply]);

  if (!generatedReply) {
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
        Awaiting agent execution to compose grounded response...
      </div>
    );
  }

  const isRevised = generatedReply.revision_count > 0;

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
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
          <Sparkles size={14} color="var(--deep-enterprise-green)" />
          <h3
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '13px',
              fontWeight: 600,
              color: 'var(--cohere-black)',
            }}
          >
            Generated Response
          </h3>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
          {isRevised && (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                padding: '2px 8px',
                borderRadius: 'var(--radius-xs)',
                backgroundColor: '#fffbeb',
                color: '#b45309',
                fontFamily: 'var(--font-mono)',
                fontSize: '10px',
                fontWeight: 600,
                border: '1px solid #fde68a',
              }}
            >
              <History size={11} />
              REVISED ({generatedReply.revision_count})
            </span>
          )}

          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              color: generatedReply.is_grounded ? 'var(--success-green)' : 'var(--coral)',
            }}
          >
            {generatedReply.is_grounded ? (
              <>
                <CheckCheck size={13} />
                GROUNDED
              </>
            ) : (
              <>
                <AlertCircle size={13} />
                UNGROUNDED
              </>
            )}
          </span>
        </div>
      </div>

      {/* Revision Banner if applicable */}
      {isRevised && (
        <div
          style={{
            padding: 'var(--space-8) var(--space-10)',
            backgroundColor: '#fffbeb',
            border: '1px solid #fef3c7',
            borderRadius: 'var(--radius-xs)',
            fontSize: '11px',
            color: '#92400e',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-6)',
          }}
        >
          <History size={13} style={{ flexShrink: 0 }} />
          <span>
            Response automatically revised after hallucinated claims failed strict grounding verification.
          </span>
        </div>
      )}

      {/* Editor Surface */}
      <div
        style={{
          border: '1px solid var(--hairline)',
          borderRadius: 'var(--radius-xs)',
          backgroundColor: isEditing ? '#ffffff' : 'var(--soft-stone)',
          padding: 'var(--space-12)',
        }}
      >
        {isEditing ? (
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={5}
            style={{
              width: '100%',
              border: 'none',
              background: 'transparent',
              outline: 'none',
              fontSize: '14px',
              fontFamily: 'var(--font-body)',
              color: 'var(--ink)',
              lineHeight: '1.5',
              resize: 'vertical',
            }}
          />
        ) : (
          <div
            style={{
              fontSize: '14px',
              lineHeight: '1.5',
              color: 'var(--ink)',
              whiteSpace: 'pre-wrap',
            }}
          >
            {text}
          </div>
        )}
      </div>

      {/* Evidence References */}
      <EvidenceReference
        evidenceIds={generatedReply.evidence_ids}
        onSelectEvidence={onSelectEvidence}
      />

      {/* Actions */}
      <ResponseActions
        isGrounded={generatedReply.is_grounded}
        decision={decision}
        isEditing={isEditing}
        onToggleEdit={() => setIsEditing(!isEditing)}
        onSend={() => onSendResponse(text)}
        onRegenerate={onRegenerate}
        onTakeOver={onTakeOver}
        isRunning={isRunning}
      />
    </div>
  );
};
