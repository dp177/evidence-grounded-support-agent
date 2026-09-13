import { useState, useCallback, useRef, useEffect } from 'react';
import { CustomChatMessage, AgentActivityStepInfo } from '../types/customChat';
import { AgentStreamEvent, ConversationMessage, MessageRole } from '../types/agent';
import { agentApi } from '../services/agentApi';

const generateCustomConversationId = (): string => {
  return `custom_${Math.random().toString(36).substring(2, 8)}`;
};

const PIPELINE_STAGES_TEMPLATE: Omit<AgentActivityStepInfo, 'id'>[] = [
  { stage: 'Conversation', label: 'Conversation history & context loaded', status: 'COMPLETED', detail: 'Conversation context prepared' },
  { stage: 'Classify', label: 'Analyzing intent & operational conversation state...', status: 'RUNNING', detail: 'Zero-shot multi-intent & state classification' },
  { stage: 'Retrieve', label: 'Searching historical precedent cases in Qdrant...', status: 'IDLE', detail: 'Dense semantic similarity search (Top 30 candidates)' },
  { stage: 'Rerank', label: 'Reranking candidates with multi-signal scorer...', status: 'IDLE', detail: 'Semantic, lexical TF-IDF, and action penalty signals' },
  { stage: 'Generate', label: 'Synthesizing evidence-grounded resolution...', status: 'IDLE', detail: 'Precedent-conditioned resolution drafting' },
  { stage: 'Ground', label: 'Auditing claims against precedent facts (Grounding)...', status: 'IDLE', detail: 'NLI hallucination prevention check' },
  { stage: 'Decide', label: 'Evaluating deterministic escalation policy...', status: 'IDLE', detail: 'Safety boundaries & auto-handle decision' },
];

export const useCustomChat = () => {
  const [conversationId, setConversationId] = useState<string>(generateCustomConversationId());
  const [messages, setMessages] = useState<CustomChatMessage[]>([]);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [lastFailedText, setLastFailedText] = useState<string | null>(null);
  // Timer for elapsed display (still used for live elapsed clock — NOT for stage faking)
  const elapsedTimerRef = useRef<any>(null);

  useEffect(() => {
    return () => {
      if (elapsedTimerRef.current) {
        clearInterval(elapsedTimerRef.current);
        elapsedTimerRef.current = null;
      }
    };
  }, []);

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

      // ── Live elapsed clock: increments every 100ms purely for the timer display ──
      // NOTE: This does NOT control stage transitions — stages transition only from real events.
      elapsedTimerRef.current = setInterval(() => {
        const elapsed = Number(((Date.now() - startTime) / 1000).toFixed(1));
        setMessages((prev) =>
          prev.map((msg) => {
            if (msg.id !== assistantMsgId || msg.activityStatus !== 'RUNNING') return msg;
            return { ...msg, elapsedSeconds: elapsed };
          })
        );
      }, 100);

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
            updateStep(1, { status: 'RUNNING', label: 'Analyzing intent & operational conversation state...' });
            break;

          case 'classify': {
            const clf = event.classification;
            const detail = (clf.status === 'AMBIGUOUS' || !clf.primary_intent)
              ? `Ambiguous (no intent) — ${(clf.confidence * 100).toFixed(0)}% conf`
              : `${clf.primary_intent} (${(clf.confidence * 100).toFixed(0)}% conf)`;
            // Complete Classify, start Retrieve
            updateStep(2, { status: 'RUNNING', label: 'Searching historical precedent cases in Qdrant...' });
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMsgId || !msg.activitySteps) return msg;
                const updatedSteps = msg.activitySteps.map((st, i) => {
                  if (i === 1) return { ...st, status: 'COMPLETED' as const, detail };
                  if (i === 2) return { ...st, status: 'RUNNING' as const };
                  return st;
                });
                return { ...msg, activitySteps: updatedSteps, partialClassification: clf };
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
                  if (i === 2) return { ...st, status: 'COMPLETED' as const, detail: `${event.candidate_count} candidates` };
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
                const updatedSteps = msg.activitySteps.map((st, i) => {
                  if (i === 4) return { ...st, status: 'COMPLETED' as const };
                  if (i === 5) return { ...st, status: 'RUNNING' as const };
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
                const g = event.grounding;
                const updatedSteps = msg.activitySteps.map((st, i) => {
                  if (i === 5) return { ...st, status: g.status === 'GROUNDED' ? 'COMPLETED' as const : 'WARNING' as const, detail: `${g.supported_claims}/${g.total_claims} claims supported` };
                  if (i === 6) return { ...st, status: 'RUNNING' as const };
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
                const esc = event.escalation;
                const updatedSteps = msg.activitySteps.map((st, i) => {
                  if (i === 6) return { ...st, status: esc.decision === 'AUTO_HANDLE' ? 'COMPLETED' as const : 'WARNING' as const, detail: esc.decision };
                  return st;
                });
                return { ...msg, activitySteps: updatedSteps, partialEscalation: esc };
              })
            );
            break;

          case 'complete': {
            // Full response arrived — finalize message and immediately unlock input
            const result = event.response;
            const finalThoughtDuration = Number(((Date.now() - startTime) / 1000).toFixed(1));
            if (elapsedTimerRef.current) {
              clearInterval(elapsedTimerRef.current);
              elapsedTimerRef.current = null;
            }
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMsgId) return msg;
                return {
                  ...msg,
                  text: result.generated_reply.reply,
                  activityStatus: 'COMPLETED',
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
            if (elapsedTimerRef.current) {
              clearInterval(elapsedTimerRef.current);
              elapsedTimerRef.current = null;
            }
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
        if (elapsedTimerRef.current) {
          clearInterval(elapsedTimerRef.current);
          elapsedTimerRef.current = null;
        }
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
