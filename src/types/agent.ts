export type MessageRole = 'CUSTOMER' | 'AGENT' | 'ASSISTANT' | 'SYSTEM';

export interface ConversationMessage {
  id: string;
  role: MessageRole;
  text: string;
  timestamp?: string;
  isCurrent?: boolean;
}

export interface ClassificationResult {
  status: 'NORMAL' | 'AMBIGUOUS' | 'HIGH_RISK' | 'OUT_OF_SCOPE';
  areas: string[];
  intents: string[];
  primary_intent: string | null;
  states: string[];
  confidence: number; // 0.00 - 1.00 (MODEL CONFIDENCE)
  multi_intent: boolean;
  taxonomy_version?: string;
}

export interface RetrievalEvidence {
  case_id: string;
  conversation_id: string;
  turn_index: number;
  rank?: number;
  similarity: number;
  customer_message: string;
  relevant_context: string;
  brand_response: string;
  doc_id?: string;
  semantic_score?: number | null;
  lexical_score?: number | null;
  intent_score?: number | null;
  state_score?: number | null;
  action_usefulness?: number | null;
  action_penalty_flag?: number | null;
  final_score?: number | null;
  rerank_score?: number | null;
}

export interface RerankingSignal {
  name: string;
  label: string;
  score?: number | null; // feature score, or null if uncomputed
  weight?: number;
  description?: string;
}

export interface RerankingResult {
  candidate_count: number;
  final_count: number;
  unique_conversations: number;
  signals: RerankingSignal[];
  ranked_cases: RetrievalEvidence[];
  weights?: Record<string, number>;
}

export interface GeneratedResponse {
  reply: string;
  evidence_ids: string[];
  is_grounded: boolean;
  revision_count: number;
  draft_reply?: string;
}

export type ClaimVerificationStatus =
  | 'CURRENT_CONVERSATION_SUPPORTED'
  | 'HISTORICAL_EVIDENCE_SUPPORTED'
  | 'BOTH'
  | 'UNSUPPORTED'
  | 'CONTRADICTED';

export interface ClaimVerification {
  id: string;
  text: string;
  source_type: 'CONVERSATION' | 'HISTORICAL_EVIDENCE' | 'INFERRED' | 'EXTRANEOUS';
  status: ClaimVerificationStatus;
  supporting_ref?: string;
}

export interface GroundingResult {
  status: 'GROUNDED' | 'REQUIRES_REVISION' | 'FAILED';
  score: number; // 0.0 - 1.0
  total_claims: number;
  supported_claims: number;
  unsupported_claims: number;
  contradicted_claims: number;
  claims: ClaimVerification[];
  unsupported_claim_details?: string[];
  revision_count: number;
}

export type EscalationDecision = 'AUTO_HANDLE' | 'HUMAN_REVIEW';
export type EscalationAction = 'RESOLVE' | 'CLARIFY' | 'ESCALATE_TO_SPECIALIST' | 'SECURITY_FREEZE';

export interface EscalationResult {
  decision: EscalationDecision;
  action: EscalationAction;
  reason_codes: string[];
  passed_gates: string[];
  blocker_reasons: string[];
  summary_for_human?: string;
}

export interface AgentTrace {
  request_id: string;
  conversation_id: string;
  classification_ms: number;
  retrieval_ms: number;
  reranker_ms: number;
  generation_ms: number;
  grounding_ms: number;
  total_ms: number;
  llm_calls: number;
}

export interface AgentResponse {
  conversation_id: string;
  classification: ClassificationResult;
  retrieval_query: {
    customer_query: string;
    context: string;
  };
  retrieved_evidence: RetrievalEvidence[];
  reranking: RerankingResult;
  generated_reply: GeneratedResponse;
  grounding: GroundingResult;
  escalation: EscalationResult;
  trace: AgentTrace;
}

export type StageName =
  | 'Conversation'
  | 'Classify'
  | 'Retrieve'
  | 'Rerank'
  | 'Generate'
  | 'Ground'
  | 'Decide';

export type StageStatus = 'IDLE' | 'RUNNING' | 'SUCCESS' | 'WARNING' | 'FAILED';

export interface StageInfo {
  name: StageName;
  status: StageStatus;
  label: string;
  details?: Record<string, unknown>;
}

export interface DemoScenario {
  id: string;
  name: string;
  description: string;
  customerInitial: string;
  conversation: ConversationMessage[];
  expectedState: {
    intent: string;
    states: string[];
    decision: EscalationDecision;
    risk?: string;
  };
  responsePayload: AgentResponse;
}

// ---------------------------------------------------------------------------
// Streaming event types emitted by the backend /api/agent/stream endpoint
// ---------------------------------------------------------------------------
export type AgentStreamEvent =
  | { type: 'conversation'; status: 'COMPLETED'; turn_count: number; customer_message: string }
  | { type: 'classify'; status: 'COMPLETED'; latency_ms: number; classification: ClassificationResult }
  | { type: 'retrieve'; status: 'COMPLETED'; latency_ms: number; candidate_count: number; query_text: string }
  | { type: 'rerank'; status: 'COMPLETED'; latency_ms: number; retrieved_evidence: RetrievalEvidence[]; reranking: RerankingResult }
  | { type: 'generate'; status: 'COMPLETED'; latency_ms: number; reply: string; draft_reply: string; revision_count: number }
  | { type: 'ground'; status: 'COMPLETED'; latency_ms: number; grounding: GroundingResult }
  | { type: 'decide'; status: 'COMPLETED'; escalation: EscalationResult }
  | { type: 'complete'; status: 'COMPLETED'; response: AgentResponse }
  | { type: 'error'; error: string };

