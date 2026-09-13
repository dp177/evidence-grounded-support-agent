import React, { useRef, useEffect, useState } from 'react';
import { useCustomChat } from '../../hooks/useCustomChat';
import { CustomChatMessage } from './CustomChatMessage';
import { CustomComposer } from './CustomComposer';
import { Bot, ArrowDown } from 'lucide-react';

export const CustomLiveChat: React.FC = () => {
  const {
    conversationId,
    messages,
    isRunning,
    sendMessage,
    newConversation,
    switchToDemoMode,
    retryLastMessage,
  } = useCustomChat();

  const scrollRef = useRef<HTMLDivElement>(null);
  const [showScrollBottom, setShowScrollBottom] = useState(false);

  // Auto-scroll when new message/activity is added
  useEffect(() => {
    if (scrollRef.current) {
      if (typeof scrollRef.current.scrollTo === 'function') {
        scrollRef.current.scrollTo({
          top: scrollRef.current.scrollHeight,
          behavior: 'smooth',
        });
      } else {
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
      }
    }
  }, [messages]);

  const handleScroll = () => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    const distanceToBottom = scrollHeight - scrollTop - clientHeight;
    setShowScrollBottom(distanceToBottom > 150);
  };

  const scrollToBottom = () => {
    if (scrollRef.current) {
      if (typeof scrollRef.current.scrollTo === 'function') {
        scrollRef.current.scrollTo({
          top: scrollRef.current.scrollHeight,
          behavior: 'smooth',
        });
      } else {
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
      }
    }
  };

  const samplePrompts = [
    'my package says delivered but I never got it and I already contacted the carrier twice',
    'someone hacked my amazon account and used my credit card',
    'I returned my item 4 days ago, when will my refund post to my card?',
  ];

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 110px)',
        backgroundColor: 'var(--canvas-white)',
        position: 'relative',
      }}
    >
      {/* Scrollable Chat Area */}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: 'var(--space-20) var(--space-16)',
        }}
      >
        <div
          style={{
            maxWidth: '960px',
            margin: '0 auto',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {messages.length === 0 ? (
            /* Clean Centered Empty State */
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                padding: 'var(--space-56) var(--space-16)',
                gap: 'var(--space-16)',
              }}
            >
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: 'var(--radius-xs)',
                  backgroundColor: 'var(--deep-enterprise-green)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ffffff',
                }}
              >
                <Bot size={24} />
              </div>

              <div>
                <h1
                  style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: '24px',
                    fontWeight: 600,
                    color: 'var(--cohere-black)',
                    letterSpacing: '-0.02em',
                  }}
                >
                  AI Support Agent
                </h1>
                <p
                  style={{
                    fontSize: '14px',
                    color: 'var(--slate)',
                    marginTop: 'var(--space-6)',
                    maxWidth: '480px',
                    lineHeight: '1.5',
                  }}
                >
                  Type a customer-support message to start.
                </p>
              </div>

              {/* Sample Prompts */}
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 'var(--space-8)',
                  width: '100%',
                  maxWidth: '560px',
                  marginTop: 'var(--space-12)',
                }}
              >
                <span className="mono-label" style={{ fontSize: '10px' }}>
                  SAMPLE INQUIRIES TO EXPLORE
                </span>
                {samplePrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => sendMessage(prompt)}
                    style={{
                      padding: '10px 14px',
                      borderRadius: 'var(--radius-xs)',
                      backgroundColor: 'var(--soft-stone)',
                      border: '1px solid var(--border-light)',
                      fontFamily: 'var(--font-body)',
                      fontSize: '13px',
                      color: 'var(--ink)',
                      textAlign: 'left',
                      cursor: 'pointer',
                      transition: 'background-color 0.15s ease',
                    }}
                  >
                    "{prompt}"
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* Message Thread */
            messages.map((msg, idx) => (
              <CustomChatMessage
                key={msg.id}
                message={msg}
                turnIndex={idx + 1}
                totalTurns={messages.length}
                onSendResponse={(text) => alert(`Message sent to customer: "${text}"`)}
                onTakeOver={() => alert(`Session ${conversationId} transferred to human tier.`)}
                onRetry={retryLastMessage}
                onSwitchToDemo={switchToDemoMode}
              />
            ))
          )}
        </div>
      </div>

      {/* Floating Scroll to Bottom button if scrolled up */}
      {showScrollBottom && (
        <button
          type="button"
          onClick={scrollToBottom}
          style={{
            position: 'absolute',
            bottom: '80px',
            right: 'calc(50% - 20px)',
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: 'var(--near-black-primary)',
            color: '#ffffff',
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            zIndex: 10,
          }}
        >
          <ArrowDown size={16} />
        </button>
      )}

      {/* Fixed Bottom Message Composer */}
      <CustomComposer
        onSendMessage={sendMessage}
        onNewConversation={newConversation}
        isRunning={isRunning}
      />
    </div>
  );
};
