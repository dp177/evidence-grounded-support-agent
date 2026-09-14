import React, { useRef, useEffect } from 'react';
import { ConversationMessage, ClassificationResult } from '../../types/agent';
import { ConversationHeader } from './ConversationHeader';
import { MessageBubble } from './MessageBubble';
import { ConversationStateCard } from './ConversationStateCard';
import { MessageComposer } from './MessageComposer';
import { MessageSquareDashed } from 'lucide-react';

interface ConversationPanelProps {
  conversationId: string;
  messages: ConversationMessage[];
  classification?: ClassificationResult | null;
  isRunning: boolean;
  onSendMessage: (text: string, runImmediately: boolean) => void;
  onReset: () => void;
}

export const ConversationPanel: React.FC<ConversationPanelProps> = ({
  conversationId,
  messages,
  classification,
  isRunning,
  onSendMessage,
  onReset,
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const isUserScrolledUpRef = useRef(false);
  const prevMessagesLengthRef = useRef(messages.length);

  const handleScroll = () => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    isUserScrolledUpRef.current = (scrollHeight - scrollTop - clientHeight) > 60;
  };

  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    if (e.deltaY < 0) {
      isUserScrolledUpRef.current = true;
    } else if (e.deltaY > 0 && scrollRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
      if (scrollHeight - scrollTop - clientHeight <= 60) {
        isUserScrolledUpRef.current = false;
      }
    }
  };

  useEffect(() => {
    if (!scrollRef.current) return;
    const isNewMessage = messages.length > prevMessagesLengthRef.current;
    prevMessagesLengthRef.current = messages.length;

    if (isUserScrolledUpRef.current && !isNewMessage) {
      return;
    }
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  const customerMessages = messages.filter((m) => m.role === 'CUSTOMER');
  const latestCustomerId = customerMessages[customerMessages.length - 1]?.id;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 180px)',
        minHeight: '680px',
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-sm)',
        overflow: 'hidden',
      }}
    >
      {/* 1. Header */}
      <ConversationHeader
        conversationId={conversationId}
        turnCount={messages.length}
        onReset={onReset}
      />

      {/* 2. Scrollable Timeline */}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        onWheel={handleWheel}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: 'var(--space-16)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-12)',
          backgroundColor: '#fafafb',
        }}
      >
        {messages.length === 0 ? (
          <div
            style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 'var(--space-8)',
              color: 'var(--muted-slate)',
              textAlign: 'center',
              padding: 'var(--space-32)',
            }}
          >
            <MessageSquareDashed size={32} color="var(--hairline)" />
            <div style={{ fontSize: '14px', fontWeight: 500, color: 'var(--slate)' }}>
              No messages in session
            </div>
            <p style={{ fontSize: '13px', maxWidth: '280px' }}>
              Send a customer message to start analysis or select a demo scenario above.
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              isLatestCustomer={msg.id === latestCustomerId}
            />
          ))
        )}
      </div>

      {/* 3. Conversation State Card */}
      <div style={{ padding: 'var(--space-12) var(--space-16)', backgroundColor: '#ffffff' }}>
        <ConversationStateCard
          classification={classification}
          turnCount={messages.length}
        />
      </div>

      {/* 4. Message Input Box */}
      <MessageComposer
        onSendMessage={onSendMessage}
        isRunning={isRunning}
      />
    </div>
  );
};
