import { AgentResponse, ConversationMessage } from '../types/agent';
import { DEMO_SCENARIOS } from '../data/demoCases';
import { IAgentApi } from './apiTypes';

export class MockAgentApi implements IAgentApi {
  isMock(): boolean {
    return true;
  }

  async runAgent(
    conversationId: string,
    messages: ConversationMessage[]
  ): Promise<AgentResponse> {
    // Simulate real pipeline network latency (400ms)
    await new Promise((resolve) => setTimeout(resolve, 450));

    const lastMessage = messages[messages.length - 1]?.text.toLowerCase() || '';
    const allCustomerText = messages
      .filter((m) => m.role === 'CUSTOMER')
      .map((m) => m.text.toLowerCase())
      .join(' ');

    // 1. Account Hacked / Security Check
    if (
      allCustomerText.includes('hacked') ||
      allCustomerText.includes('unauthorized') ||
      allCustomerText.includes('card') && allCustomerText.includes('used')
    ) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-account-hacked')!;
      return {
        ...scenario.responsePayload,
        conversation_id: conversationId,
      };
    }

    // 2. Ambiguous Complaint Check
    if (
      allCustomerText.includes('done with amazon') ||
      (allCustomerText.includes('fix this') && allCustomerText.length < 35) ||
      allCustomerText.includes('horrible service')
    ) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-ambiguous-complaint')!;
      return {
        ...scenario.responsePayload,
        conversation_id: conversationId,
      };
    }

    // 3. Delivered Not Received Check
    if (
      allCustomerText.includes('porch') ||
      (allCustomerText.includes('delivered') && allCustomerText.includes('nothing is there')) ||
      allCustomerText.includes('not received')
    ) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-delivered-not-received')!;
      return {
        ...scenario.responsePayload,
        conversation_id: conversationId,
      };
    }

    // 4. Cancel Order Check
    if (
      allCustomerText.includes('cancel') ||
      allCustomerText.includes('accidental') ||
      allCustomerText.includes('duplicate of the same')
    ) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-cancel-order')!;
      return {
        ...scenario.responsePayload,
        conversation_id: conversationId,
      };
    }

    // 5. Refund Status Check
    if (
      allCustomerText.includes('refund') ||
      allCustomerText.includes('returned') ||
      allCustomerText.includes('warehouse')
    ) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-refund-status')!;
      return {
        ...scenario.responsePayload,
        conversation_id: conversationId,
      };
    }

    // 6. Default: Delivery Delayed with progressive multi-turn state detection
    const defaultScenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-delivery-delayed')!;
    const payload = JSON.parse(JSON.stringify(defaultScenario.responsePayload)) as AgentResponse;
    payload.conversation_id = conversationId;

    const dynamicStates = ['WAITING_WINDOW_EXCEEDED'];

    if (allCustomerText.includes('checked') || allCustomerText.includes('tracking')) {
      dynamicStates.unshift('TRACKING_ALREADY_CHECKED');
    }

    if (allCustomerText.includes('carrier') || allCustomerText.includes('ups') || allCustomerText.includes('fedex')) {
      dynamicStates.push('CARRIER_ALREADY_CONTACTED');
    }

    payload.classification.states = dynamicStates;

    // Update query reflection
    payload.retrieval_query.customer_query = messages[messages.length - 1]?.text || payload.retrieval_query.customer_query;

    return payload;
  }
}

export const mockAgentApi = new MockAgentApi();
