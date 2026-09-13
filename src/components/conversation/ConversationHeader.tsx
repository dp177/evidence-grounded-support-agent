import React from 'react';
import { RotateCcw, User } from 'lucide-react';

interface ConversationHeaderProps {
  conversationId: string;
  turnCount: number;
  onReset: () => void;
}

export const ConversationHeader: React.FC<ConversationHeaderProps> = ({
  conversationId,
  turnCount,
  onReset,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 'var(--space-12) var(--space-16)',
        borderBottom: '1px solid var(--border-light)',
        backgroundColor: '#ffffff',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
        <div
          style={{
            width: '24px',
            height: '24px',
            borderRadius: 'var(--radius-xs)',
            backgroundColor: 'var(--soft-stone)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--ink)',
          }}
        >
          <User size={14} />
        </div>
        <div>
          <h2
            style={{
              fontSize: '14px',
              fontWeight: 600,
              fontFamily: 'var(--font-display)',
              letterSpacing: '-0.01em',
              color: 'var(--cohere-black)',
            }}
          >
            Customer Conversation
          </h2>
          <span
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              color: 'var(--muted-slate)',
            }}
          >
            ID: {conversationId} • {turnCount} turns
          </span>
        </div>
      </div>

      <button
        onClick={onReset}
        title="Reset conversation and start new session"
        className="btn-secondary"
        style={{
          fontSize: '12px',
          padding: '4px 8px',
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          textDecoration: 'none',
          color: 'var(--slate)',
        }}
      >
        <RotateCcw size={12} />
        Reset
      </button>
    </div>
  );
};
