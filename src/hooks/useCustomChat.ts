import { useState, useCallback } from 'react';
import { CustomChatMessage, AgentActivityStepInfo } from '../types/customChat';
import { ConversationMessage, MessageRole } from '../types/agent';
import { agentApi } from '../services/agentApi';

const generateCustomConversationId = (): string => {
  return `custom_${Math.random().toString(36).substring(2, 8)}`;
};

// Exact 8-stage pipeline requested for live execution
const INITIAL_STEPS_TEMPLATE: Omit<AgentActivityStepInfo, 'id'>[] = [
  { stage: 'Conversation', label: 'Conversation loaded', status: 'COMPLETED' },
  { stage: 'Classify', label: 'Analyzing conversation', status: 'RUNNING' },
  { stage: 'State', label: 'Updating conversation state', status: 'IDLE' },
  { stage: 'Retrieve', label: 'Searching historical support cases', status: 'IDLE' },
  { stage: 'Rerank', label: 'Selecting relevant precedents', status: 'IDLE' },
  { stage: 'Generate', label: 'Drafting response', status: 'IDLE' },
  { stage: 'Ground', label: 'Checking grounding', status: 'IDLE' },
  { stage: 'Decide', label: 'Making support decision', status: 'IDLE' },
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

      // Build payload for API preserving full multi-turn conversation
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

      // Simulated progressive activity transitions across the 8 stages
      let stepIdx = 1;
      const stepInterval = setInterval(() => {
        stepIdx++;
        if (stepIdx < initialSteps.length) {
          setMessages((prev) =>
            prev.map((msg) => {
              if (msg.id !== assistantMsgId || !msg.activitySteps) return msg;
              const updatedSteps = msg.activitySteps.map((st, i) => {
                if (i < stepIdx) return { ...st, status: 'COMPLETED' as const };
                if (i === stepIdx) return { ...st, status: 'RUNNING' as const };
                return { ...st, status: 'IDLE' as const };
              });
              return { ...msg, activitySteps: updatedSteps };
            })
          );
        }
      }, 55);

      try {
        const result = await agentApi.runAgent(conversationId, conversationHistory);
        clearInterval(stepInterval);

        setMessages((prev) =>
          prev.map((msg) => {
            if (msg.id !== assistantMsgId || !msg.activitySteps) return msg;

            // Structured completed steps conforming to requirement specifications
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
                label: 'Classification completed',
                status: 'COMPLETED',
                detail: `${result.classification.primary_intent} (${(result.classification.confidence * 100).toFixed(0)}% conf)`,
              },
              {
                id: 's2',
                stage: 'State',
                label: 'State updated',
                status: 'COMPLETED',
                detail: result.classification.states.join(', ') || 'Normal',
              },
              {
                id: 's3',
                stage: 'Retrieve',
                label: 'Retrieved historical cases',
                status: 'COMPLETED',
                detail: `${result.retrieved_evidence.length} precedents`,
              },
              {
                id: 's4',
                stage: 'Rerank',
                label: 'Reranked evidence',
                status: 'COMPLETED',
                detail: `${result.reranking.unique_conversations} threads`,
              },
              {
                id: 's5',
                stage: 'Generate',
                label: 'Response generated',
                status: 'COMPLETED',
              },
              {
                id: 's6',
                stage: 'Ground',
                label: 'Grounding verified',
                status: result.grounding.status === 'GROUNDED' ? 'COMPLETED' : 'WARNING',
                detail: `${result.grounding.supported_claims}/${result.grounding.total_claims} claims`,
              },
              {
                id: 's7',
                stage: 'Decide',
                label: 'Decision completed',
                status: result.escalation.decision === 'AUTO_HANDLE' ? 'COMPLETED' : 'WARNING',
                detail: result.escalation.decision,
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
              text: '', // Never fabricate a response on failure
              activityStatus: 'FAILED',
              activitySteps: [
                ...(msg.activitySteps?.map((st) =>
                  st.status === 'RUNNING' ? { ...st, status: 'FAILED' as const } : st
                ) || []),
                {
                  id: 'err_step',
                  stage: 'Decide',
                  label: '⚠ Agent could not complete the request',
                  status: 'FAILED',
                  detail: `Reason: ${errMsg}`,
                },
              ],
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
