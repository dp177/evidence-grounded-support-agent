import React from 'react';
import { Send, RefreshCw, Edit3, AlertOctagon, UserCheck } from 'lucide-react';
import { EscalationDecision } from '../../types/agent';

interface ResponseActionsProps {
  isGrounded: boolean;
  decision?: EscalationDecision;
  isEditing: boolean;
  onToggleEdit: () => void;
  onSend: () => void;
  onRegenerate: () => void;
  onTakeOver?: () => void;
  isRunning?: boolean;
}

export const ResponseActions: React.FC<ResponseActionsProps> = ({
  isGrounded,
  decision,
  isEditing,
  onToggleEdit,
  onSend,
  onRegenerate,
  onTakeOver,
  isRunning = false,
}) => {
  const isAutoHandle = decision === 'AUTO_HANDLE';
  const canSend = isGrounded && isAutoHandle;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingTop: 'var(--space-10)',
        borderTop: '1px solid var(--border-light)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
        <button
          type="button"
          onClick={onToggleEdit}
          className="btn-pill-outline"
          style={{ fontSize: '12px', padding: '5px 12px' }}
        >
          <Edit3 size={13} />
          {isEditing ? 'Preview' : 'Edit'}
        </button>

        <button
          type="button"
          onClick={onRegenerate}
          disabled={isRunning}
          className="btn-pill-outline"
          style={{ fontSize: '12px', padding: '5px 12px' }}
        >
          <RefreshCw size={13} />
          Regenerate
        </button>
      </div>

      <div>
        {canSend ? (
          <button
            type="button"
            onClick={onSend}
            disabled={isRunning}
            className="btn-primary"
            style={{ fontSize: '13px', padding: '8px 20px' }}
          >
            <Send size={13} />
            Send Response
          </button>
        ) : !isGrounded ? (
          <button
            type="button"
            onClick={onRegenerate}
            disabled={isRunning}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 16px',
              borderRadius: 'var(--radius-pill)',
              backgroundColor: 'rgba(255, 119, 89, 0.15)',
              color: 'var(--coral)',
              border: '1px solid var(--coral)',
              fontFamily: 'var(--font-body)',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <AlertOctagon size={14} />
            Grounding Issue → Revise
          </button>
        ) : (
          <button
            type="button"
            onClick={onTakeOver}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 18px',
              borderRadius: 'var(--radius-pill)',
              backgroundColor: '#fff7ed',
              color: '#c2410c',
              border: '1px solid #fdba74',
              fontFamily: 'var(--font-body)',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <UserCheck size={14} />
            Take Over Conversation
          </button>
        )}
      </div>
    </div>
  );
};
