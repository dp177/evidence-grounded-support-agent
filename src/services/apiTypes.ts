import { AgentResponse, AgentStreamEvent, ConversationMessage } from '../types/agent';

export interface IAgentApi {
  runAgent(conversationId: string, messages: ConversationMessage[]): Promise<AgentResponse>;
  runAgentStream(
    conversationId: string,
    messages: ConversationMessage[],
    onEvent: (event: AgentStreamEvent) => void
  ): Promise<AgentResponse>;
  isMock(): boolean;
}
