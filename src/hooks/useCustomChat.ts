import { useState, useCallback, useRef, useEffect } from 'react';
import { CustomChatMessage, AgentActivityStepInfo } from '../types/customChat';
import { AgentStreamEvent, ConversationMessage, MessageRole } from '../types/agent';
import { agentApi } from '../services/agentApi';

const generateCustomConversationId = (): string => {
  return `custom_${Math.random().toString(36).substring(2, 8)}`;
};

const PIPELINE_STAGES_TEMPLATE: Omit<AgentActivityStepInfo, 'id'>[] = [
  { stage: 'Conversation', label: 'Conversation history & context loaded', status: 'COMPLETED', detail: 'Context initialized' },
  { stage: 'Classify', label: 'Analyzing intent & operational conversation state', status: 'RUNNING', detail: 'Intent & state classification' },
  { stage: 'Retrieve', label: 'Searching historical precedent cases in Qdrant', status: 'IDLE', detail: 'Semantic vector search (Top 30 candidates)' },
  { stage: 'Rerank', label: 'Reranking candidates with multi-signal scorer', status: 'IDLE', detail: 'Multi-signal scoring & filtering' },
  { stage: 'Generate', label: 'Synthesizing evidence-grounded resolution', status: 'IDLE', detail: 'Evidence-conditioned generation' },
  { stage: 'Ground', label: 'Auditing claims against precedent facts', status: 'IDLE', detail: 'NLI grounding verification' },
  { stage: 'Decide', label: 'Evaluating deterministic escalation policy', status: 'IDLE', detail: 'Safety boundaries & decision' },
];

export const useCustomChat = () => {
  const [conversationId, setConversationId] = useState<string>(generateCustomConversationId());
  const [messages, setMessages] = useState<CustomChatMessage[]>([]);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [lastFailedText, setLastFailedText] = useState<string | null>(null);
  const newConversation = useCallback(() => {
    setConversationId(generateCustomConversationId());
    setMessages([]);
    setIsRunning(false);
    setLastFailedText(null);
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || isRunning) return;

      const customerMsgId = `cust_${Date.now()}`;
      const assistantMsgId = `asst_${Date.now()}`;
      const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const startTime = Date.now();

      const newCustomerMsg: CustomChatMessage = {
        id: customerMsgId,
        role: 'CUSTOMER',
        text,
        timestamp: timeStr,
      };

      const initialSteps: AgentActivityStepInfo[] = PIPELINE_STAGES_TEMPLATE.map((s, idx) => ({
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
        elapsedSeconds: 0,
      };

      setMessages((prev) => [...prev, newCustomerMsg, newAssistantMsg]);
      setIsRunning(true);
      setLastFailedText(null);

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

      // ── Helper: update a specific stage step in activitySteps ──
      const updateStep = (stageIdx: number, patch: Partial<AgentActivityStepInfo>) => {
        setMessages((prev) =>
          prev.map((msg) => {
            if (msg.id !== assistantMsgId || !msg.activitySteps) return msg;
            const updatedSteps = msg.activitySteps.map((st, i) => {
              if (i < stageIdx) return { ...st, status: 'COMPLETED' as const };
              if (i === stageIdx) return { ...st, ...patch };
              return st;
            });
            return { ...msg, activitySteps: updatedSteps };
          })
        );
      };

      // ── SSE event handler: drives ALL stage transitions from real backend events ──
      const onEvent = (event: AgentStreamEvent) => {
        switch (event.type) {
          case 'conversation':
            // Step 0 (Conversation) is already COMPLETED by default in initialSteps;
            // Mark step 1 (Classify) as RUNNING.
            updateStep(1, { status: 'RUNNING', label: 'Analyzing intent & operational conversation state' });
            break;

          case 'classify': {
            const clf = event.classification;
            const isAmbiguous = clf.status === 'AMBIGUOUS' || !clf.primary_intent;
            const detail = isAmbiguous
              ? `Ambiguous (no intent) — ${(clf.confidence * 100).toFixed(0)}% conf`
              : `${clf.primary_intent} (${(clf.confidence * 100).toFixed(0)}% conf)`;

            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMsgId || !msg.activitySteps) return msg;

                if (isAmbiguous) {
                  // Swap to 5-step clarification activity pipeline
                  const ambiguousSteps: AgentActivityStepInfo[] = [
                    { id: `step_0_${Date.now()}`, stage: 'Conversation', label: 'Conversation context loaded', status: 'COMPLETED', detail: 'Context initialized' },
                    { id: `step_1_${Date.now()}`, stage: 'Classify', label: 'Analyzing intent & operational conversation state', status: 'COMPLETED', detail },
                    { id: `step_2_${Date.now()}`, stage: 'Generate', label: 'Clarification being drafted', status: 'RUNNING', detail: 'Drafting clarifying question' },
                    { id: `step_3_${Date.now()}`, stage: 'Ground', label: 'Checking response safety', status: 'IDLE', detail: 'Safety & policy audit' },
                    { id: `step_4_${Date.now()}`, stage: 'Decide', label: 'Final response ready', status: 'IDLE', detail: 'Clarification response ready' },
                  ];
                  return { ...msg, activitySteps: ambiguousSteps, partialClassification: clf };
                } else {
                  // Normal RAG pipeline: complete Classify, start Retrieve
                  const updatedSteps = msg.activitySteps.map((st, i) => {
                    if (i === 1) return { ...st, status: 'COMPLETED' as const, detail };
                    if (i === 2) return { ...st, status: 'RUNNING' as const };
                    return st;
                  });
                  return { ...msg, activitySteps: updatedSteps, partialClassification: clf };
                }
              })
            );
            break;
          }

          case 'retrieve':
            // Complete Retrieve, start Rerank
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMsgId || !msg.activitySteps) return msg;
                const updatedSteps = msg.activitySteps.map((st, i) => {
                  if (i === 2) return { ...st, status: 'COMPLETED' as const, detail: `${event.candidate_count} candidates retrieved` };
                  if (i === 3) return { ...st, status: 'RUNNING' as const };
                  return st;
                });
                return { ...msg, activitySteps: updatedSteps };
              })
            );
            break;

          case 'rerank':
            // Complete Rerank, start Generate
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMsgId || !msg.activitySteps) return msg;
                const updatedSteps = msg.activitySteps.map((st, i) => {
                  if (i === 3) return { ...st, status: 'COMPLETED' as const, detail: `${event.retrieved_evidence.length} precedents selected` };
                  if (i === 4) return { ...st, status: 'RUNNING' as const };
                  return st;
                });
                return {
                  ...msg,
                  activitySteps: updatedSteps,
                  partialEvidence: event.retrieved_evidence,
                  partialReranking: event.reranking,
                };
              })
            );
            break;

          case 'generate':
            // Complete Generate, start Ground
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMsgId || !msg.activitySteps) return msg;
                const isAmbiguous = msg.activitySteps.length === 5;
                const genIdx = isAmbiguous ? 2 : 4;
                const nextIdx = isAmbiguous ? 3 : 5;
                const genDetail = isAmbiguous ? 'Clarification drafted' : 'Resolution drafted';
                const updatedSteps = msg.activitySteps.map((st, i) => {
                  if (i === genIdx) return { ...st, status: 'COMPLETED' as const, detail: genDetail };
                  if (i === nextIdx) return { ...st, status: 'RUNNING' as const };
                  return st;
                });
                return {
                  ...msg,
                  text: event.reply,
                  activitySteps: updatedSteps,
                };
              })
            );
            break;

          case 'ground':
            // Complete Ground, start Decide
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMsgId || !msg.activitySteps) return msg;
                const isAmbiguous = msg.activitySteps.length === 5;
                const grndIdx = isAmbiguous ? 3 : 5;
                const nextIdx = isAmbiguous ? 4 : 6;
                const g = event.grounding;
                const grndDetail = isAmbiguous
                  ? 'Response safety verified'
                  : `${g.supported_claims}/${g.total_claims} claims supported · Grounded`;
                const updatedSteps = msg.activitySteps.map((st, i) => {
                  if (i === grndIdx) return {
                    ...st,
                    status: g.status === 'GROUNDED' ? 'COMPLETED' as const : 'WARNING' as const,
                    detail: grndDetail,
                  };
                  if (i === nextIdx) return { ...st, status: 'RUNNING' as const };
                  return st;
                });
                return { ...msg, activitySteps: updatedSteps, partialGrounding: g };
              })
            );
            break;

          case 'decide':
            // Complete Decide
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMsgId || !msg.activitySteps) return msg;
                const isAmbiguous = msg.activitySteps.length === 5;
                const decIdx = isAmbiguous ? 4 : 6;
                const esc = event.escalation;
                const decDetail = isAmbiguous
                  ? 'Clarification ready'
                  : `${esc.decision} · ${esc.action}`;
                const updatedSteps = msg.activitySteps.map((st, i) => {
                  if (i === decIdx) return {
                    ...st,
                    status: esc.decision === 'AUTO_HANDLE' ? 'COMPLETED' as const : 'WARNING' as const,
                    detail: decDetail,
                  };
                  return st;
                });
                return { ...msg, activitySteps: updatedSteps, partialEscalation: esc };
              })
            );
            break;

          case 'complete': {
            // Full response arrived — finalize message, ensure all steps are resolved, and unlock input
            const result = event.response;
            const finalThoughtDuration = Number(((Date.now() - startTime) / 1000).toFixed(1));
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMsgId) return msg;
                const finalizedSteps = msg.activitySteps?.map((st) => {
                  if (st.status === 'RUNNING' || st.status === 'IDLE') {
                    return { ...st, status: 'COMPLETED' as const };
                  }
                  return st;
                });
                return {
                  ...msg,
                  text: result.generated_reply.reply,
                  activityStatus: 'COMPLETED',
                  activitySteps: finalizedSteps || msg.activitySteps,
                  agentResponse: result,
                  thoughtDuration: finalThoughtDuration,
                  elapsedSeconds: undefined,
                  // Clear partials — full response is now present
                  partialClassification: undefined,
                  partialEvidence: undefined,
                  partialReranking: undefined,
                  partialGrounding: undefined,
                  partialEscalation: undefined,
                };
              })
            );
            // Unlock input immediately — don't wait for the TCP stream to close
            setIsRunning(false);
            break;
          }


          case 'error':
            // Backend emitted an error event mid-stream
            setLastFailedText(text);
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMsgId) return msg;
                return {
                  ...msg,
                  text: '',
                  activityStatus: 'FAILED',
                  activitySteps: [
                    { id: 'err_stream', stage: 'Decide', label: 'Stream error', status: 'FAILED', detail: event.error },
                  ],
                };
              })
            );
            break;
        }
      };

      try {
        await agentApi.runAgentStream(conversationId, conversationHistory, onEvent);
      } catch (err: unknown) {
        const errMsg = err instanceof Error ? err.message : 'Backend execution failed';
        setLastFailedText(text);

        setMessages((prev) =>
          prev.map((msg) => {
            if (msg.id !== assistantMsgId) return msg;
            return {
              ...msg,
              text: '', // Never fabricate response on error
              activityStatus: 'FAILED',
              activitySteps: [
                {
                  id: 'err_live',
                  stage: 'Decide',
                  label: errMsg.includes('LIVE AGENT UNAVAILABLE')
                    ? 'LIVE AGENT UNAVAILABLE'
                    : '⚠ Agent could not complete the request',
                  status: 'FAILED',
                  detail: errMsg,
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

  const switchToDemoMode = useCallback(() => {
    agentApi.setMockMode(true);
    if (lastFailedText) {
      // Remove the failed assistant message and retry with mock
      setMessages((prev) => prev.filter((m) => m.activityStatus !== 'FAILED'));
      sendMessage(lastFailedText);
    }
  }, [lastFailedText, sendMessage]);

  const retryLastMessage = useCallback(() => {
    if (lastFailedText) {
      setMessages((prev) => prev.filter((m) => m.activityStatus !== 'FAILED'));
      sendMessage(lastFailedText);
    }
  }, [lastFailedText, sendMessage]);

  return {
    conversationId,
    messages,
    isRunning,
    sendMessage,
    newConversation,
    switchToDemoMode,
    retryLastMessage,
  };
};
