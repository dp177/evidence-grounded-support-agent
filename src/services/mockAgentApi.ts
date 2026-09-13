import { AgentResponse, AgentStreamEvent, ConversationMessage } from '../types/agent';
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

    const latestMsg = (messages[messages.length - 1]?.text || '').trim();
    const latestLower = latestMsg.toLowerCase();
    const allCustomerText = messages
      .filter((m) => m.role === 'CUSTOMER')
      .map((m) => m.text.toLowerCase())
      .join(' ');
    const customerTurnCount = messages.filter((m) => m.role === 'CUSTOMER').length;

    // 1. Account Hacked / Security Check (Deterministic High-Risk)
    if (
      allCustomerText.includes('hacked') ||
      allCustomerText.includes('unauthorized') ||
      (allCustomerText.includes('card') && allCustomerText.includes('used')) ||
      allCustomerText.includes('stolen')
    ) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-account-hacked')!;
      const payload = JSON.parse(JSON.stringify(scenario.responsePayload)) as AgentResponse;
      payload.conversation_id = conversationId;
      payload.retrieval_query.customer_query = latestMsg;
      return payload;
    }

    // 2. Ambiguous Complaint Check
    if (
      latestLower === 'hi' ||
      latestLower === 'hello' ||
      latestLower === 'help' ||
      allCustomerText.includes('done with amazon') ||
      (allCustomerText.includes('fix this') && allCustomerText.length < 35) ||
      allCustomerText.includes('horrible service')
    ) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-ambiguous-complaint')!;
      const payload = JSON.parse(JSON.stringify(scenario.responsePayload)) as AgentResponse;
      payload.conversation_id = conversationId;
      payload.retrieval_query.customer_query = latestMsg;
      return payload;
    }

    // 3. Multi-Turn Delivery Dispute Progression
    if (
      allCustomerText.includes('delivered') ||
      allCustomerText.includes('package') ||
      allCustomerText.includes('carrier') ||
      allCustomerText.includes('porch') ||
      allCustomerText.includes('order')
    ) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-delivered-not-received')!;
      const payload = JSON.parse(JSON.stringify(scenario.responsePayload)) as AgentResponse;
      payload.conversation_id = conversationId;
      payload.retrieval_query.customer_query = latestMsg;

      // Multi-Turn Turn 2: Wrong Address / Misdelivery Concern
      if (
        latestLower.includes('wrong address') ||
        latestLower.includes('misdeliver') ||
        latestLower.includes('neighbor') ||
        latestLower.includes('address')
      ) {
        payload.classification.primary_intent = 'DELIVERY_STATUS_DISPUTED';
        payload.classification.states = [
          'CARRIER_MARKED_DELIVERED',
          'PACKAGE_NOT_FOUND',
          'CARRIER_ALREADY_CONTACTED',
          'POTENTIAL_MISDELIVERY',
        ];
        payload.classification.confidence = 0.94;
        payload.generated_reply.reply =
          "I understand your concern that the package may have been delivered to the wrong address. Since the courier tracking indicates completed delivery to your postal code, we can check the driver's GPS delivery scan and safe-place drop photo. Could you please confirm your street number and whether any neighbors have received it?";
        payload.grounding.claims = [
          {
            id: 'c1',
            text: 'Customer reports potential misdelivery to incorrect address',
            source_type: 'CONVERSATION',
            status: 'CURRENT_CONVERSATION_SUPPORTED',
          },
          {
            id: 'c2',
            text: 'Carrier GPS delivery scan and safe-place drop photo can be investigated',
            source_type: 'HISTORICAL_EVIDENCE',
            status: 'HISTORICAL_EVIDENCE_SUPPORTED',
          },
          {
            id: 'c3',
            text: 'Requesting confirmation of street address and neighbor check',
            source_type: 'HISTORICAL_EVIDENCE',
            status: 'BOTH',
          },
        ];
        payload.grounding.total_claims = 3;
        payload.grounding.supported_claims = 3;
        payload.escalation.action = 'CLARIFY';
        return payload;
      }

      // Multi-Turn Turn 3: "What should I do now?" / "Still not here" -> Escalation or Replacement
      if (
        latestLower.includes('what should i do') ||
        latestLower.includes('what now') ||
        latestLower.includes('what do i do') ||
        latestLower.includes('still not here') ||
        customerTurnCount >= 3
      ) {
        payload.classification.primary_intent = 'DELIVERY_STATUS_DISPUTED';
        payload.classification.states = [
          'CARRIER_MARKED_DELIVERED',
          'PACKAGE_NOT_FOUND',
          'CARRIER_ALREADY_CONTACTED',
          'WAITING_WINDOW_EXCEEDED',
        ];
        payload.classification.confidence = 0.96;
        payload.generated_reply.reply =
          "Thank you for confirming. Because the carrier has been contacted twice and the waiting window has expired without locating your parcel, I can initiate a free replacement order or issue a full refund to your original payment method. Please let me know which option you prefer.";
        payload.grounding.claims = [
          {
            id: 'c1',
            text: 'Carrier contacted multiple times and waiting window expired',
            source_type: 'CONVERSATION',
            status: 'CURRENT_CONVERSATION_SUPPORTED',
          },
          {
            id: 'c2',
            text: 'Eligible for replacement order or full refund to original payment method',
            source_type: 'HISTORICAL_EVIDENCE',
            status: 'HISTORICAL_EVIDENCE_SUPPORTED',
          },
        ];
        payload.grounding.total_claims = 2;
        payload.grounding.supported_claims = 2;
        payload.escalation.action = 'RESOLVE';
        return payload;
      }

      // Turn 1 Default: Initial Delivery Dispute
      const dynamicStates = ['CARRIER_MARKED_DELIVERED', 'PACKAGE_NOT_FOUND'];
      if (allCustomerText.includes('checked') || allCustomerText.includes('tracking')) {
        dynamicStates.push('TRACKING_ALREADY_CHECKED');
      }
      if (allCustomerText.includes('carrier') || allCustomerText.includes('called') || allCustomerText.includes('contacted')) {
        dynamicStates.push('CARRIER_ALREADY_CONTACTED');
      }
      payload.classification.states = dynamicStates;
      return payload;
    }

    // 4. Cancel Order Check
    if (allCustomerText.includes('cancel') || allCustomerText.includes('accidental')) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-cancel-order')!;
      const payload = JSON.parse(JSON.stringify(scenario.responsePayload)) as AgentResponse;
      payload.conversation_id = conversationId;
      payload.retrieval_query.customer_query = latestMsg;
      return payload;
    }

    // 5. Refund Status Check
    if (allCustomerText.includes('refund') || allCustomerText.includes('returned')) {
      const scenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-refund-status')!;
      const payload = JSON.parse(JSON.stringify(scenario.responsePayload)) as AgentResponse;
      payload.conversation_id = conversationId;
      payload.retrieval_query.customer_query = latestMsg;
      return payload;
    }

    // 6. Generic Fallback
    const defaultScenario = DEMO_SCENARIOS.find((s) => s.id === 'demo-delivery-delayed')!;
    const payload = JSON.parse(JSON.stringify(defaultScenario.responsePayload)) as AgentResponse;
    payload.conversation_id = conversationId;
    payload.retrieval_query.customer_query = latestMsg;
    return payload;
  }

  async runAgentStream(
    conversationId: string,
    messages: ConversationMessage[],
    onEvent: (event: AgentStreamEvent) => void
  ): Promise<AgentResponse> {
    // In mock mode: simulate stage events sequentially with realistic delays
    // so the progressive stacking UI works the same as in live mode.
    const delay = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms));

    // Get the full mock response first (internally)
    const fullResponse = await this.runAgent(conversationId, messages);

    // Emit: conversation
    onEvent({ type: 'conversation', status: 'COMPLETED', turn_count: messages.length, customer_message: messages[messages.length - 1]?.text ?? '' });
    await delay(120);

    // Emit: classify
    onEvent({ type: 'classify', status: 'COMPLETED', latency_ms: 800, classification: fullResponse.classification });
    await delay(200);

    // Emit: retrieve (only for NORMAL queries with evidence)
    if (fullResponse.retrieved_evidence && fullResponse.retrieved_evidence.length > 0) {
      onEvent({ type: 'retrieve', status: 'COMPLETED', latency_ms: 450, candidate_count: fullResponse.reranking.candidate_count, query_text: fullResponse.retrieval_query.customer_query });
      await delay(150);

      // Emit: rerank
      onEvent({ type: 'rerank', status: 'COMPLETED', latency_ms: 320, retrieved_evidence: fullResponse.retrieved_evidence, reranking: fullResponse.reranking });
      await delay(150);
    }

    // Emit: generate
    onEvent({ type: 'generate', status: 'COMPLETED', latency_ms: 1200, reply: fullResponse.generated_reply.reply, draft_reply: fullResponse.generated_reply.draft_reply ?? '', revision_count: fullResponse.generated_reply.revision_count });
    await delay(200);

    // Emit: ground
    onEvent({ type: 'ground', status: 'COMPLETED', latency_ms: 600, grounding: fullResponse.grounding });
    await delay(100);

    // Emit: decide
    onEvent({ type: 'decide', status: 'COMPLETED', escalation: fullResponse.escalation });
    await delay(60);

    // Emit: complete
    onEvent({ type: 'complete', status: 'COMPLETED', response: fullResponse });

    return fullResponse;
  }
}

export const mockAgentApi = new MockAgentApi();
