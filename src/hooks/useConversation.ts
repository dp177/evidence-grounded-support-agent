import { useState, useCallback } from 'react';
import { ConversationMessage, DemoScenario, MessageRole } from '../types/agent';

export interface UseConversationReturn {
  conversationId: string;
  messages: ConversationMessage[];
  addMessage: (text: string, role?: MessageRole) => ConversationMessage;
  appendAgentMessage: (text: string) => void;
  resetConversation: () => void;
  loadScenario: (scenario: DemoScenario) => void;
  getCurrentMessage: () => ConversationMessage | undefined;
}

const generateConversationId = (): string => {
  return `conv_${Math.random().toString(36).substring(2, 9)}`;
};

export const useConversation = (initialConversationId?: string): UseConversationReturn => {
  const [conversationId, setConversationId] = useState<string>(
    initialConversationId || generateConversationId()
  );
  const [messages, setMessages] = useState<ConversationMessage[]>([]);

  const addMessage = useCallback(
    (text: string, role: MessageRole = 'CUSTOMER'): ConversationMessage => {
      const newMessage: ConversationMessage = {
        id: `msg_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
        role,
        text,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isCurrent: role === 'CUSTOMER',
      };

      setMessages((prev) => {
        // Mark previous messages as not current
        const updated = prev.map((m) => ({ ...m, isCurrent: false }));
        return [...updated, newMessage];
      });

      return newMessage;
    },
    []
  );

  const appendAgentMessage = useCallback((text: string) => {
    const newMessage: ConversationMessage = {
      id: `msg_${Date.now()}_agent`,
      role: 'AGENT',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isCurrent: false,
    };

    setMessages((prev) => [...prev, newMessage]);
  }, []);

  const resetConversation = useCallback(() => {
    setConversationId(generateConversationId());
    setMessages([]);
  }, []);

  const loadScenario = useCallback((scenario: DemoScenario) => {
    setConversationId(`conv_${scenario.id.replace('demo-', '')}_${Math.floor(Math.random() * 9000 + 1000)}`);
    setMessages(scenario.conversation.map((m) => ({ ...m })));
  }, []);

  const getCurrentMessage = useCallback((): ConversationMessage | undefined => {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'CUSTOMER') {
        return messages[i];
      }
    }
    return undefined;
  }, [messages]);

  return {
    conversationId,
    messages,
    addMessage,
    appendAgentMessage,
    resetConversation,
    loadScenario,
    getCurrentMessage,
  };
};
