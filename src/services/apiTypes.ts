import { AgentResponse, ConversationMessage } from '../types/agent';

export interface IAgentApi {
  runAgent(conversationId: string, messages: ConversationMessage[]): Promise<AgentResponse>;
  isMock(): boolean;
}
