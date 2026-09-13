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
  if (import.meta.env.VITE_USE_MOCK_AGENT !== undefined) {
    return import.meta.env.VITE_USE_MOCK_AGENT === 'true';
  }
  return true;
};

export class ProductionAgentApi implements IAgentApi {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_AGENT_API_URL || '/api';
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

    // Live endpoint execution per requirement specification: POST /api/agent/message
    try {
      const endpoint = this.baseUrl.endsWith('/')
        ? `${this.baseUrl}agent/message`
        : `${this.baseUrl}/agent/message`;

      const response = await fetch(endpoint, {
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
