import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, RotateCcw, Loader2 } from 'lucide-react';

interface CustomComposerProps {
  onSendMessage: (text: string) => void;
  onNewConversation: () => void;
  isRunning: boolean;
}

export const CustomComposer: React.FC<CustomComposerProps> = ({
  onSendMessage,
  onNewConversation,
  isRunning,
}) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isRunning) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      style={{
        position: 'sticky',
        bottom: 0,
        backgroundColor: 'var(--canvas-white)',
        padding: 'var(--space-12) 0 var(--space-20) 0',
        borderTop: '1px solid var(--border-light)',
      }}
    >
      <div
        style={{
          maxWidth: '960px',
          margin: '0 auto',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-8)',
          padding: '0 var(--space-16)',
        }}
      >
        {/* Input box */}
        <div
          style={{
            position: 'relative',
            display: 'flex',
            alignItems: 'flex-end',
            backgroundColor: '#ffffff',
            border: '1px solid var(--hairline)',
            borderRadius: '24px',
            padding: '10px 16px',
            boxShadow: '0 2px 6px rgba(0, 0, 0, 0.04)',
            transition: 'border-color 0.15s ease',
          }}
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isRunning}
            placeholder="Type a customer message... (e.g. My package says delivered but I never received it)"
            rows={1}
            style={{
              flex: 1,
              border: 'none',
              outline: 'none',
              background: 'transparent',
              fontSize: '14px',
              fontFamily: 'var(--font-body)',
              color: 'var(--ink)',
              resize: 'none',
              maxHeight: '120px',
              lineHeight: '1.5',
              paddingRight: 'var(--space-8)',
            }}
          />

          <button
            type="button"
            onClick={() => handleSubmit()}
            disabled={!input.trim() || isRunning}
            title="Send Message (Enter)"
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: input.trim() && !isRunning ? 'var(--near-black-primary)' : 'var(--card-border)',
              color: input.trim() && !isRunning ? '#ffffff' : 'var(--muted-slate)',
              border: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: input.trim() && !isRunning ? 'pointer' : 'not-allowed',
              transition: 'all 0.15s ease',
              flexShrink: 0,
            }}
          >
            {isRunning ? (
              <Loader2 size={15} className="spin-animation" />
            ) : (
              <ArrowUp size={16} />
            )}
          </button>
        </div>

        {/* Footer controls: New Conversation & info */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '11px',
            fontFamily: 'var(--font-mono)',
            color: 'var(--muted-slate)',
            padding: '0 8px',
          }}
        >
          <button
            type="button"
            id="btn-new-conversation"
            onClick={onNewConversation}
            className="btn-pill-outline"
            style={{
              fontSize: '11px',
              padding: '4px 10px',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              cursor: 'pointer',
            }}
          >
            <RotateCcw size={11} />
            ＋ New conversation
          </button>

          <span>
            {isRunning ? 'Agent is working...' : 'Press Enter to send • Shift + Enter for new line'}
          </span>
        </div>
      </div>
    </div>
  );
};
