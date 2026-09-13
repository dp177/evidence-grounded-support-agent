import { useState, useCallback } from 'react';
import { AgentResponse, ConversationMessage, StageInfo, StageName, StageStatus } from '../types/agent';
import { agentApi } from '../services/agentApi';

export type AgentExecutionStatus = 'idle' | 'running' | 'success' | 'warning' | 'failed';

const INITIAL_STAGES: StageInfo[] = [
  { name: 'Conversation', status: 'IDLE', label: '1. Conversation' },
  { name: 'Classify', status: 'IDLE', label: '2. Classify' },
  { name: 'Retrieve', status: 'IDLE', label: '3. Retrieve' },
  { name: 'Rerank', status: 'IDLE', label: '4. Rerank' },
  { name: 'Generate', status: 'IDLE', label: '5. Generate' },
  { name: 'Ground', status: 'IDLE', label: '6. Ground' },
  { name: 'Decide', status: 'IDLE', label: '7. Decide' },
];

export interface UseAgentReturn {
  status: AgentExecutionStatus;
  currentStage: StageName | null;
  stages: StageInfo[];
  response: AgentResponse | null;
  error: string | null;
  runAgent: (conversationId: string, messages: ConversationMessage[]) => Promise<AgentResponse | null>;
  reset: () => void;
  loadDirectResponse: (payload: AgentResponse) => void;
}

export const useAgent = (): UseAgentReturn => {
  const [status, setStatus] = useState<AgentExecutionStatus>('idle');
  const [currentStage, setCurrentStage] = useState<StageName | null>(null);
  const [stages, setStages] = useState<StageInfo[]>(INITIAL_STAGES);
  const [response, setResponse] = useState<AgentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const reset = useCallback(() => {
    setStatus('idle');
    setCurrentStage(null);
    setStages(INITIAL_STAGES.map((s) => ({ ...s, status: 'IDLE' })));
    setResponse(null);
    setError(null);
  }, []);

  const loadDirectResponse = useCallback((payload: AgentResponse) => {
    setResponse(payload);
    setStatus(payload.escalation.decision === 'AUTO_HANDLE' ? 'success' : 'warning');
    setStages([
      { name: 'Conversation', status: 'SUCCESS', label: '1. Conversation' },
      { name: 'Classify', status: 'SUCCESS', label: '2. Classify', details: payload.classification as unknown as Record<string, unknown> },
      { name: 'Retrieve', status: 'SUCCESS', label: '3. Retrieve', details: { count: payload.retrieved_evidence.length, query: payload.retrieval_query } },
      { name: 'Rerank', status: 'SUCCESS', label: '4. Rerank', details: payload.reranking as unknown as Record<string, unknown> },
      { name: 'Generate', status: 'SUCCESS', label: '5. Generate', details: payload.generated_reply as unknown as Record<string, unknown> },
      { name: 'Ground', status: payload.grounding.status === 'GROUNDED' ? 'SUCCESS' : 'WARNING', label: '6. Ground', details: payload.grounding as unknown as Record<string, unknown> },
      { name: 'Decide', status: payload.escalation.decision === 'AUTO_HANDLE' ? 'SUCCESS' : 'WARNING', label: '7. Decide', details: payload.escalation as unknown as Record<string, unknown> },
    ]);
  }, []);

  const runAgent = useCallback(
    async (
      conversationId: string,
      messages: ConversationMessage[]
    ): Promise<AgentResponse | null> => {
      setStatus('running');
      setError(null);

      // Progressive stage visual simulation for UI feedback
      const stageSequence: StageName[] = [
        'Conversation',
        'Classify',
        'Retrieve',
        'Rerank',
        'Generate',
        'Ground',
        'Decide',
      ];

      setStages((prev) =>
        prev.map((s) => ({
          ...s,
          status: s.name === 'Conversation' ? 'SUCCESS' : 'IDLE',
        }))
      );

      let stageIdx = 1;
      const interval = setInterval(() => {
        if (stageIdx < stageSequence.length) {
          const activeName = stageSequence[stageIdx];
          setCurrentStage(activeName);
          setStages((prev) =>
            prev.map((s, idx) => {
              if (idx < stageIdx) return { ...s, status: 'SUCCESS' as StageStatus };
              if (idx === stageIdx) return { ...s, status: 'RUNNING' as StageStatus };
              return { ...s, status: 'IDLE' as StageStatus };
            })
          );
          stageIdx++;
        }
      }, 70);

      try {
        const result = await agentApi.runAgent(conversationId, messages);
        clearInterval(interval);

        setResponse(result);
        const finalStatus: AgentExecutionStatus =
          result.escalation.decision === 'AUTO_HANDLE' ? 'success' : 'warning';
        setStatus(finalStatus);
        setCurrentStage(null);

        setStages([
          { name: 'Conversation', status: 'SUCCESS', label: '1. Conversation' },
          { name: 'Classify', status: 'SUCCESS', label: '2. Classify', details: result.classification as unknown as Record<string, unknown> },
          { name: 'Retrieve', status: 'SUCCESS', label: '3. Retrieve', details: { count: result.retrieved_evidence.length, query: result.retrieval_query } },
          { name: 'Rerank', status: 'SUCCESS', label: '4. Rerank', details: result.reranking as unknown as Record<string, unknown> },
          { name: 'Generate', status: 'SUCCESS', label: '5. Generate', details: result.generated_reply as unknown as Record<string, unknown> },
          {
            name: 'Ground',
            status: result.grounding.status === 'GROUNDED' ? 'SUCCESS' : 'WARNING',
            label: '6. Ground',
            details: result.grounding as unknown as Record<string, unknown>,
          },
          {
            name: 'Decide',
            status: result.escalation.decision === 'AUTO_HANDLE' ? 'SUCCESS' : 'WARNING',
            label: '7. Decide',
            details: result.escalation as unknown as Record<string, unknown>,
          },
        ]);

        return result;
      } catch (err: unknown) {
        clearInterval(interval);
        setStatus('failed');
        setCurrentStage(null);
        const msg = err instanceof Error ? err.message : 'Agent pipeline execution failed';
        setError(msg);
        setStages((prev) =>
          prev.map((s) => (s.status === 'RUNNING' ? { ...s, status: 'FAILED' } : s))
        );
        return null;
      }
    },
    []
  );

  return {
    status,
    currentStage,
    stages,
    response,
    error,
    runAgent,
    reset,
    loadDirectResponse,
  };
};
