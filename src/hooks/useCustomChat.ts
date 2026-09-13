import { useState, useCallback } from 'react';
import { CustomChatMessage, AgentActivityStepInfo } from '../types/customChat';
import { ConversationMessage, MessageRole } from '../types/agent';
import { agentApi } from '../services/agentApi';

const generateCustomConversationId = (): string => {
  return `custom_${Math.random().toString(36).substring(2, 8)}`;
};

const INITIAL_STEPS_TEMPLATE: Omit<AgentActivityStepInfo, 'id'>[] = [
  { stage: 'Conversation', label: 'Reading conversation & context', status: 'RUNNING' },
  { stage: 'Classify', label: 'Identifying support intent & state', status: 'IDLE' },
  { stage: 'Retrieve', label: 'Searching historical support cases', status: 'IDLE' },
  { stage: 'Rerank', label: 'Selecting strongest precedents', status: 'IDLE' },
  { stage: 'Generate', label: 'Drafting grounded response', status: 'IDLE' },
  { stage: 'Ground', label: 'Checking response claims against evidence', status: 'IDLE' },
  { stage: 'Decide', label: 'Evaluating safety & escalation rules', status: 'IDLE' },
];

export const useCustomChat = () => {
  const [conversationId, setConversationId] = useState<string>(generateCustomConversationId());
  const [messages, setMessages] = useState<CustomChatMessage[]>([]);
  const [isRunning, setIsRunning] = useState<boolean>(false);

  const newConversation = useCallback(() => {
    setConversationId(generateCustomConversationId());
    setMessages([]);
    setIsRunning(false);
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || isRunning) return;

      const customerMsgId = `cust_${Date.now()}`;
      const assistantMsgId = `asst_${Date.now()}`;
      const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      const newCustomerMsg: CustomChatMessage = {
        id: customerMsgId,
        role: 'CUSTOMER',
        text,
        timestamp: timeStr,
      };

      const initialSteps: AgentActivityStepInfo[] = INITIAL_STEPS_TEMPLATE.map((s, idx) => ({
        ...s,
        id: `step_${idx}_${Date.now()}`,
      }));

      const newAssistantMsg: CustomChatMessage = {
        id: assistantMsgId,
        role: 'ASSISTANT',
        text: '',
        timestamp: timeStr,
        activityStatus: 'RUNNING',
        activitySteps: initialSteps,
      };

      setMessages((prev) => [...prev, newCustomerMsg, newAssistantMsg]);
      setIsRunning(true);

      // Build payload for API
      const conversationHistory: ConversationMessage[] = [
        ...messages
          .filter((m) => m.text)
          .map((m) => ({
            id: m.id,
            role: (m.role === 'ASSISTANT' ? 'AGENT' : 'CUSTOMER') as MessageRole,
            text: m.text,
          })),
        { id: customerMsgId, role: 'CUSTOMER' as const, text },
      ];

      // Simulated progressive activity transitions while backend runs
      let stepIdx = 0;
      const stepInterval = setInterval(() => {
        stepIdx++;
        if (stepIdx < initialSteps.length) {
          setMessages((prev) =>
            prev.map((msg) => {
              if (msg.id !== assistantMsgId || !msg.activitySteps) return msg;
              const updatedSteps = msg.activitySteps.map((st, i) => {
                if (i < stepIdx) return { ...st, status: 'COMPLETED' as const };
                if (i === stepIdx) return { ...st, status: 'RUNNING' as const };
                return st;
              });
              return { ...msg, activitySteps: updatedSteps };
            })
          );
        }
      }, 70);

      try {
        const result = await agentApi.runAgent(conversationId, conversationHistory);
        clearInterval(stepInterval);

        setMessages((prev) =>
          prev.map((msg) => {
            if (msg.id !== assistantMsgId || !msg.activitySteps) return msg;
            const completedSteps: AgentActivityStepInfo[] = [
              {
                id: 's0',
                stage: 'Conversation',
                label: 'Conversation loaded',
                status: 'COMPLETED',
                detail: `${conversationHistory.length} turns`,
              },
              {
                id: 's1',
                stage: 'Classify',
                label: `Intent: ${result.classification.primary_intent}`,
                status: 'COMPLETED',
                detail: `${(result.classification.confidence * 100).toFixed(0)}% confidence`,
              },
              {
                id: 's2',
                stage: 'Retrieve',
                label: 'Historical cases retrieved',
                status: 'COMPLETED',
                detail: `${result.retrieved_evidence.length} candidates`,
              },
              {
                id: 's3',
                stage: 'Rerank',
                label: 'Precedents selected',
                status: 'COMPLETED',
                detail: `${result.reranking.unique_conversations} threads`,
              },
              {
                id: 's4',
                stage: 'Generate',
                label: 'Response drafted',
                status: 'COMPLETED',
              },
              {
                id: 's5',
                stage: 'Ground',
                label: `Grounding verified (${result.grounding.supported_claims}/${result.grounding.total_claims} claims)`,
                status: result.grounding.status === 'GROUNDED' ? 'COMPLETED' : 'WARNING',
                detail: result.grounding.revision_count > 0 ? `revised ${result.grounding.revision_count}x` : undefined,
              },
              {
                id: 's6',
                stage: 'Decide',
                label: `Policy Gate: ${result.escalation.decision}`,
                status: result.escalation.decision === 'AUTO_HANDLE' ? 'COMPLETED' : 'WARNING',
                detail: result.escalation.action,
              },
            ];

            return {
              ...msg,
              text: result.generated_reply.reply,
              activityStatus: 'COMPLETED',
              activitySteps: completedSteps,
              agentResponse: result,
            };
          })
        );
      } catch (err: unknown) {
        clearInterval(stepInterval);
        const errMsg = err instanceof Error ? err.message : 'Pipeline execution failed';
        setMessages((prev) =>
          prev.map((msg) => {
            if (msg.id !== assistantMsgId) return msg;
            return {
              ...msg,
              text: 'A temporary error occurred while processing this customer message. Please retry or transfer to a human operator.',
              activityStatus: 'FAILED',
              activitySteps: msg.activitySteps?.map((st) =>
                st.status === 'RUNNING' ? { ...st, status: 'FAILED' } : st
              ),
            };
          })
        );
      } finally {
        setIsRunning(false);
      }
    },
    [conversationId, isRunning, messages]
  );

  return {
    conversationId,
    messages,
    isRunning,
    sendMessage,
    newConversation,
  };
};
