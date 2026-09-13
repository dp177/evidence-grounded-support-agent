import React from 'react';
import { ConversationMessage } from '../../types/agent';
import { User, Bot } from 'lucide-react';

interface MessageBubbleProps {
  message: ConversationMessage;
  isLatestCustomer?: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isLatestCustomer = false,
}) => {
  const isCustomer = message.role === 'CUSTOMER';

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-4)',
        padding: 'var(--space-12) var(--space-16)',
        borderRadius: 'var(--radius-sm)',
        backgroundColor: isLatestCustomer
          ? 'var(--pale-blue-wash)'
          : isCustomer
          ? '#ffffff'
          : 'var(--soft-stone)',
        border: isLatestCustomer
          ? '1px solid var(--action-blue)'
          : '1px solid var(--border-light)',
        transition: 'all 0.15s ease',
      }}
    >
      {/* Header: Role & Timestamp */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '11px',
          fontFamily: 'var(--font-mono)',
          color: 'var(--muted-slate)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
          {isCustomer ? (
            <User size={12} color={isLatestCustomer ? 'var(--action-blue)' : 'var(--slate)'} />
          ) : (
            <Bot size={12} color="var(--deep-enterprise-green)" />
          )}
          <strong
            style={{
              color: isLatestCustomer
                ? 'var(--action-blue)'
                : isCustomer
                ? 'var(--ink)'
                : 'var(--deep-enterprise-green)',
              letterSpacing: '0.2px',
            }}
          >
            {isCustomer ? 'CUSTOMER' : 'AMAZON SUPPORT AGENT'}
          </strong>

          {isLatestCustomer && (
            <span
              style={{
                backgroundColor: 'rgba(24, 99, 220, 0.12)',
                color: 'var(--action-blue)',
                padding: '1px 6px',
                borderRadius: 'var(--radius-xs)',
                fontSize: '10px',
                fontWeight: 600,
              }}
            >
              CURRENT FOCUS
            </span>
          )}
        </div>

        {message.timestamp && <span>{message.timestamp}</span>}
      </div>

      {/* Message Text */}
      <div
        style={{
          fontSize: '14px',
          lineHeight: '1.5',
          color: 'var(--ink)',
          wordBreak: 'break-word',
          whiteSpace: 'pre-wrap',
        }}
      >
        {message.text}
      </div>
    </div>
  );
};
