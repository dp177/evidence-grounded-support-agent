import React, { useState } from 'react';
import { Send, Play, Loader2 } from 'lucide-react';

interface MessageComposerProps {
  onSendMessage: (text: string, runImmediately: boolean) => void;
  isRunning: boolean;
  disabled?: boolean;
}

export const MessageComposer: React.FC<MessageComposerProps> = ({
  onSendMessage,
  isRunning,
  disabled = false,
}) => {
  const [inputText, setInputText] = useState('');

  const handleSendOnly = () => {
    if (!inputText.trim() || isRunning || disabled) return;
    onSendMessage(inputText.trim(), false);
    setInputText('');
  };

  const handleRunAgent = () => {
    if (!inputText.trim() || isRunning || disabled) return;
    onSendMessage(inputText.trim(), true);
    setInputText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleRunAgent();
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-8)',
        backgroundColor: '#ffffff',
        borderTop: '1px solid var(--border-light)',
        padding: 'var(--space-12) var(--space-16)',
      }}
    >
      <textarea
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a customer message..."
        rows={3}
        disabled={isRunning || disabled}
        style={{
          width: '100%',
          padding: 'var(--space-10) var(--space-12)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--hairline)',
          fontFamily: 'var(--font-body)',
          fontSize: '14px',
          color: 'var(--ink)',
          resize: 'none',
          outline: 'none',
          backgroundColor: isRunning ? 'var(--surface-hover)' : '#ffffff',
        }}
      />

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <span
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            color: 'var(--muted-slate)',
          }}
        >
          Press Enter to Run Agent
        </span>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
          <button
            type="button"
            onClick={handleSendOnly}
            disabled={!inputText.trim() || isRunning || disabled}
            className="btn-pill-outline"
            style={{ fontSize: '13px', padding: '6px 14px' }}
          >
            <Send size={13} />
            Add Message
          </button>

          <button
            type="button"
            onClick={handleRunAgent}
            disabled={!inputText.trim() || isRunning || disabled}
            className="btn-primary"
            style={{ fontSize: '13px', padding: '7px 18px' }}
          >
            {isRunning ? (
              <>
                <Loader2 size={14} className="spin-animation" />
                Analyzing...
              </>
            ) : (
              <>
                <Play size={13} />
                Run Agent
              </>
            )}
          </button>
        </div>
      </div>

      <style>{`
        .spin-animation {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
