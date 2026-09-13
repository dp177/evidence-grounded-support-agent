import { AgentResponse, AgentStreamEvent, ConversationMessage } from '../types/agent';
import { IAgentApi } from './apiTypes';
import { mockAgentApi } from './mockAgentApi';

// Determine initial mode strictly from environment or user setting
const getInitialMockMode = (): boolean => {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('HIVIER_USE_MOCK_AGENT');
    if (stored !== null) {
      return stored === 'true';
    }
  }
  // If explicitly configured via VITE_USE_MOCK_AGENT
  if (typeof import.meta !== 'undefined' && import.meta.env?.VITE_USE_MOCK_AGENT !== undefined) {
    return import.meta.env.VITE_USE_MOCK_AGENT === 'true';
  }
  // In test environment default to true for deterministic mock isolation
  if (typeof process !== 'undefined' && process.env?.NODE_ENV === 'test') {
    return true;
  }
  // Default to live backend
  return false;
};

export class ProductionAgentApi implements IAgentApi {
  private baseUrl: string;
  private mockMode: boolean;

  constructor() {
    this.baseUrl = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_AGENT_API_URL) || '';
    this.mockMode = getInitialMockMode();
  }

  isMock(): boolean {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('HIVIER_USE_MOCK_AGENT');
      if (stored !== null) {
        return stored === 'true';
      }
    }
    return this.mockMode;
  }

  setMockMode(enableMock: boolean): void {
    this.mockMode = enableMock;
    if (typeof window !== 'undefined') {
      localStorage.setItem('HIVIER_USE_MOCK_AGENT', enableMock ? 'true' : 'false');
    }
  }

  private _buildEndpoint(path: string): string {
    if (this.baseUrl) {
      return this.baseUrl.endsWith('/')
        ? `${this.baseUrl}${path.replace(/^\//, '')}`
        : `${this.baseUrl}${path}`;
    }
    return `/api${path}`;
  }

  private _buildMessages(messages: ConversationMessage[]) {
    return messages.map((m) => ({
      role: (m.role.toLowerCase() === 'assistant' || m.role.toLowerCase() === 'agent') ? 'assistant' : 'customer',
      content: m.text,
    }));
  }

  async runAgent(
    conversationId: string,
    messages: ConversationMessage[]
  ): Promise<AgentResponse> {
    // 1. Explicit Mock Mode
    if (this.isMock()) {
      return mockAgentApi.runAgent(conversationId, messages);
    }

    // 2. Real Live Mode -> POST /api/agent/message
    const endpoint = this._buildEndpoint('/agent/message');
    const payload = {
      conversation_id: conversationId,
      messages: this._buildMessages(messages),
    };

    let response: Response;
    try {
      response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } catch (networkErr: unknown) {
      const errDetail = networkErr instanceof Error ? networkErr.message : 'Network connection refused';
      // DO NOT silently fall back to mock. Throw explicit error per requirements.
      throw new Error(`LIVE AGENT UNAVAILABLE: Failed to reach backend at ${endpoint} (${errDetail}).`);
    }

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status} ${response.statusText}`;
      try {
        const errorJson = await response.json();
        if (errorJson?.error) errorDetail = errorJson.error;
      } catch { /* use default statusText */ }
      throw new Error(`LIVE AGENT UNAVAILABLE: ${errorDetail}`);
    }

    const data: AgentResponse = await response.json();
    return data;
  }

  async runAgentStream(
    conversationId: string,
    messages: ConversationMessage[],
    onEvent: (event: AgentStreamEvent) => void
  ): Promise<AgentResponse> {
    // Mock mode: delegate to mockAgentApi
    if (this.isMock()) {
      return mockAgentApi.runAgentStream(conversationId, messages, onEvent);
    }

    // Live mode: POST /api/agent/stream and parse SSE
    const endpoint = this._buildEndpoint('/agent/stream');
    const payload = {
      conversation_id: conversationId,
      messages: this._buildMessages(messages),
    };

    let response: Response;
    try {
      response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } catch (networkErr: unknown) {
      const errDetail = networkErr instanceof Error ? networkErr.message : 'Network connection refused';
      throw new Error(`LIVE AGENT UNAVAILABLE: Failed to reach backend at ${endpoint} (${errDetail}).`);
    }

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status} ${response.statusText}`;
      try {
        const errorJson = await response.json();
        if (errorJson?.error) errorDetail = errorJson.error;
      } catch { /* use default */ }
      throw new Error(`LIVE AGENT UNAVAILABLE: ${errorDetail}`);
    }

    if (!response.body) {
      throw new Error('LIVE AGENT UNAVAILABLE: Response body is null (streaming not supported).');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let finalResponse: AgentResponse | null = null;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // SSE blocks are separated by \n\n
      const blocks = buffer.split('\n\n');
      // Keep the last incomplete block in buffer
      buffer = blocks.pop() ?? '';

      for (const block of blocks) {
        const dataLine = block.split('\n').find((l) => l.startsWith('data: '));
        if (!dataLine) continue;

        const raw = dataLine.slice('data: '.length).trim();
        if (raw === '[DONE]') break;

        try {
          const event = JSON.parse(raw) as AgentStreamEvent;
          onEvent(event);
          if (event.type === 'complete') {
            finalResponse = (event as { type: 'complete'; status: 'COMPLETED'; response: AgentResponse }).response;
          }
        } catch {
          // Malformed SSE line — skip silently
        }
      }
    }

    if (!finalResponse) {
      throw new Error('LIVE AGENT UNAVAILABLE: Stream ended without a complete event.');
    }
    return finalResponse;
  }
}

export const agentApi = new ProductionAgentApi();
