import { AgentResponse, ConversationMessage } from '../types/agent';
import { IAgentApi } from './apiTypes';
import { mockAgentApi } from './mockAgentApi';

// Controlled via environment variable or localStorage toggle
const isMockMode = (): boolean => {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('HIVIER_USE_MOCK_AGENT');
    if (stored !== null) {
      return stored === 'true';
    }
  }
  // Default to true for deterministic frontend independence as specified in requirements
  return true;
};

export class ProductionAgentApi implements IAgentApi {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_AGENT_API_URL || 'http://localhost:8000/api/v1';
  }

  isMock(): boolean {
    return isMockMode();
  }

  async runAgent(
    conversationId: string,
    messages: ConversationMessage[]
  ): Promise<AgentResponse> {
    if (this.isMock()) {
      return mockAgentApi.runAgent(conversationId, messages);
    }

    // Live endpoint execution
    try {
      const response = await fetch(`${this.baseUrl}/agent/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          messages,
        }),
      });

      if (!response.ok) {
        throw new Error(`Agent API request failed with status: ${response.status}`);
      }

      const data: AgentResponse = await response.json();
      return data;
    } catch (err) {
      console.warn('Live Agent API unreachable, falling back to deterministic mock:', err);
      return mockAgentApi.runAgent(conversationId, messages);
    }
  }
}

export const agentApi = new ProductionAgentApi();
