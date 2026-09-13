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
    await new Promise((resolve) => setTimeout(resolve, 400));

    const latestMsg = messages[messages.length - 1]?.text || '';
    const allCustomerText = messages
      .filter((m) => m.role === 'CUSTOMER')
      .map((m) => m.text.toLowerCase())
      .join(' ');

    // 1. Account Hacked / Security Check
    if (
      allCustomerText.includes('hacked') ||
      allCustomerText.includes('unauthorized') ||
      (allCustomerText.includes('card') && allCustomerText.includes('used')) ||
      allCustomerText.includes('stolen')
    ) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-account-hacked')!;
      return {
        ...scenario.responsePayload,
        conversation_id: conversationId,
        retrieval_query: {
          customer_query: latestMsg,
          context: 'Customer reports compromised credentials and potential unauthorized transaction.',
        },
      };
    }

    // 2. Ambiguous Complaint Check
    if (
      latestMsg.trim().toLowerCase() === 'hi' ||
      latestMsg.trim().toLowerCase() === 'hello' ||
      latestMsg.trim().toLowerCase() === 'help' ||
      allCustomerText.includes('done with amazon') ||
      (allCustomerText.includes('fix this') && allCustomerText.length < 35) ||
      allCustomerText.includes('horrible service')
    ) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-ambiguous-complaint')!;
      return {
        ...scenario.responsePayload,
        conversation_id: conversationId,
        retrieval_query: {
          customer_query: latestMsg,
          context: 'Customer submitted an ambiguous inquiry without order identification or problem detail.',
        },
      };
    }

    // 3. Delivered Not Received Check
    if (
      allCustomerText.includes('porch') ||
      (allCustomerText.includes('delivered') && (allCustomerText.includes('never') || allCustomerText.includes('nothing') || allCustomerText.includes('not received') || allCustomerText.includes('not got it') || allCustomerText.includes('never got it')))
    ) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-delivered-not-received')!;
      const payload = JSON.parse(JSON.stringify(scenario.responsePayload)) as AgentResponse;
      payload.conversation_id = conversationId;
      payload.retrieval_query.customer_query = latestMsg;

      const dynamicStates = ['CARRIER_MARKED_DELIVERED', 'PACKAGE_NOT_FOUND'];
      if (allCustomerText.includes('carrier') || allCustomerText.includes('ups') || allCustomerText.includes('fedex') || allCustomerText.includes('called') || allCustomerText.includes('contacted')) {
        dynamicStates.push('CARRIER_ALREADY_CONTACTED');
      }
      if (allCustomerText.includes('36 hours') || allCustomerText.includes('days') || allCustomerText.includes('still not here')) {
        dynamicStates.push('WAITING_WINDOW_EXCEEDED');
      }
      payload.classification.states = dynamicStates;
      return payload;
    }

    // 4. Cancel Order Check
    if (
      allCustomerText.includes('cancel') ||
      allCustomerText.includes('accidental') ||
      allCustomerText.includes('duplicate')
    ) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-cancel-order')!;
      return {
        ...scenario.responsePayload,
        conversation_id: conversationId,
        retrieval_query: {
          customer_query: latestMsg,
          context: 'Customer requested cancellation of order prior to carrier dispatch.',
        },
      };
    }

    // 5. Refund Status Check
    if (
      allCustomerText.includes('refund') ||
      allCustomerText.includes('returned') ||
      allCustomerText.includes('warehouse') ||
      allCustomerText.includes('money back')
    ) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-refund-status')!;
      return {
        ...scenario.responsePayload,
        conversation_id: conversationId,
        retrieval_query: {
          customer_query: latestMsg,
          context: 'Customer inquiry regarding warehouse return processing and credit timeline.',
        },
      };
    }

    // 6. Default Dynamic Delivery / Late Order Handling
    const defaultScenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-delivery-delayed')!;
    const payload = JSON.parse(JSON.stringify(defaultScenario.responsePayload)) as AgentResponse;
    payload.conversation_id = conversationId;
    payload.retrieval_query.customer_query = latestMsg;

    const dynamicStates = ['WAITING_WINDOW_EXCEEDED'];

    if (allCustomerText.includes('checked') || allCustomerText.includes('tracking')) {
      dynamicStates.unshift('TRACKING_ALREADY_CHECKED');
    }

    if (allCustomerText.includes('carrier') || allCustomerText.includes('ups') || allCustomerText.includes('fedex') || allCustomerText.includes('called') || allCustomerText.includes('contacted')) {
      dynamicStates.push('CARRIER_ALREADY_CONTACTED');
    }

    if (allCustomerText.includes('still') || allCustomerText.includes('yesterday') || allCustomerText.includes('late')) {
      if (!dynamicStates.includes('WAITING_WINDOW_EXCEEDED')) {
        dynamicStates.push('WAITING_WINDOW_EXCEEDED');
      }
    }

    payload.classification.states = dynamicStates;

    return payload;
  }
}

export const mockAgentApi = new MockAgentApi();
