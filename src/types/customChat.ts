import { AgentResponse, StageName } from './agent';

export type ActivityStepStatus = 'IDLE' | 'RUNNING' | 'COMPLETED' | 'WARNING' | 'FAILED';

export interface AgentActivityStepInfo {
  id: string;
  stage: StageName | 'State';
  label: string;
  status: ActivityStepStatus;
  detail?: string;
  timestamp?: string;
}

export interface CustomChatMessage {
  id: string;
  role: 'CUSTOMER' | 'ASSISTANT';
  text: string;
  timestamp: string;
  activityStatus?: 'IDLE' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  activitySteps?: AgentActivityStepInfo[];
  agentResponse?: AgentResponse;
  isLatest?: boolean;
}

export type AppMode = 'DEMO_SCENARIOS' | 'CUSTOM_LIVE';
