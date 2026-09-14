import React, { useState } from 'react';
import { RerankingSignal as IRerankingSignal } from '../../types/agent';
import { Info, ChevronDown, ChevronUp, AlertTriangle, ArrowRight } from 'lucide-react';

interface RankingSignalProps {
  signal: IRerankingSignal;
  currentIntent?: string | null;
  currentStates?: string[];
}

interface SignalExplanation {
  whatItMeans: string;
  howWeCalculateIt: string;
  pipelineSteps: string[];
  whatItDoes: string;
  configuredWeight: string;
  limitation: string;
}

const SIGNAL_EXPLANATIONS: Record<string, SignalExplanation> = {
  semantic: {
    whatItMeans:
      'Cosine similarity between the current retrieval query embedding and this historical document embedding.',
    howWeCalculateIt:
      'The current inquiry (and conversation context) is embedded into a dense 384-dimensional vector using the configured sentence-transformers/all-MiniLM-L6-v2 model. Qdrant vector database computes Cosine Similarity between this vector and stored historical document embeddings.',
    pipelineSteps: [
      'CURRENT QUERY + CONTEXT',
      'all-MiniLM-L6-v2 (384-dim Embedding)',
      'COSINE SIMILARITY (Qdrant Vector Index)',
      'DENSE SIMILARITY SCORE',
    ],
    whatItDoes:
      'Serves as the primary relevance anchor for finding conceptually similar support conversations.',
    configuredWeight: 'Weight: 1.0 (configs/reranking.yaml)',
    limitation:
      'This is a geometric cosine similarity feature score between vector embeddings, not a probability or accuracy percentage.',
  },
  lexical: {
    whatItMeans:
      'Measures keyword overlap between the current customer query and the historical customer message using TF-IDF cosine similarity.',
    howWeCalculateIt:
      'Computed using scikit-learn TfidfVectorizer with generic Amazon support stop words de-emphasized ("order", "package", "delivery", "refund", "help", "amazon", "please", "thanks"). Evaluates TF-IDF cosine similarity between the query token vector and candidate message token vector.',
    pipelineSteps: [
      'CURRENT QUERY TOKENS',
      'TF-IDF VECTORIZER (Generic Stop Words Filtered)',
      'COSINE SIMILARITY ON TOKEN MATRICES',
      'LEXICAL OVERLAP FEATURE SCORE',
    ],
    whatItDoes:
      'Rewards candidates that share rare domain terminology, carrier names, or exact error descriptions.',
    configuredWeight: 'Weight: 0.3 (configs/reranking.yaml)',
    limitation:
      'This is a TF-IDF cosine feature score, not a count or percentage of matched words.',
  },
  intent: {
    whatItMeans:
      'Compatibility signal between the current predicted intent and the historical candidate. This is not a verified historical intent label.',
    howWeCalculateIt:
      'The LLM Intent Classifier predicts the current customer\'s primary intent and broad area from Taxonomy V1. The candidate reranker then checks for category intersection against available metadata on the historical candidate.',
    pipelineSteps: [
      'CURRENT PREDICTED INTENT',
      'TAXONOMY INTENT DEFINITION',
      'COMPATIBILITY EVALUATION (Category Intersection)',
      'INTENT COMPATIBILITY SCORE',
    ],
    whatItDoes:
      'Boosts candidates that align with the specific support issue category being handled.',
    configuredWeight: 'Weight: 0.2 (configs/reranking.yaml)',
    limitation:
      'Historical retrieval documents do not have trusted full-corpus intent labels. This score therefore estimates compatibility rather than performing label equality. We never invent historical intent labels.',
  },
  area: {
    whatItMeans:
      'Domain area alignment between customer issue area (e.g. DELIVERY_ISSUES, REFUND_ISSUES) and candidate.',
    howWeCalculateIt:
      'Taxonomy domain mapping evaluates whether the historical candidate matches the predicted operational area.',
    pipelineSteps: [
      'CURRENT PREDICTED AREA',
      'TAXONOMY DOMAIN CLASSIFICATION',
      'AREA COMPATIBILITY EVALUATION',
      'AREA COMPATIBILITY SCORE',
    ],
    whatItDoes:
      'Ensures candidate cases match the high-level domain area.',
    configuredWeight: 'Weight: 0.1 (configs/reranking.yaml)',
    limitation:
      'Deterministic taxonomy domain matching, not a probability.',
  },
  state: {
    whatItMeans:
      'Inferred compatibility signal. The historical case does not necessarily have a human-verified state label.',
    howWeCalculateIt:
      'The conversation state engine predicts operational progression states (e.g. CARRIER_ALREADY_CONTACTED, TRACKING_ALREADY_CHECKED, WAITING_WINDOW_EXCEEDED). The reranker checks for state feature overlap with candidate context.',
    pipelineSteps: [
      'CURRENT CONVERSATION STATE',
      'HISTORICAL OPERATIONAL EVIDENCE',
      'STATE COMPATIBILITY CHECK',
      'STATE COMPATIBILITY SCORE',
    ],
    whatItDoes:
      'Ensures the retrieved precedent reflects the same operational progression (e.g. carrier already contacted vs first contact).',
    configuredWeight: 'Weight: 0.1 (configs/reranking.yaml)',
    limitation:
      'Inferred compatibility signal — not a human-verified historical label.',
  },
  action_usefulness: {
    whatItMeans:
      'Boilerplate penalty evaluation. Historical brand responses containing deflection phrases receive a penalty (-0.2); specific operational responses receive full usefulness (1.00).',
    howWeCalculateIt:
      'Scans the historical Amazon brand response for generic deflection boilerplate patterns ("reach us via phone or chat", "send us a dm", "dm us", "click the link below"). If generic boilerplate is detected, an action penalty flag is set. Specific operational responses with resolution guidance receive full usefulness (1.00).',
    pipelineSteps: [
      'HISTORICAL AMAZON RESPONSE',
      'BOILERPLATE REGEX AUDIT (Deflection Detection)',
      'ACTIONABILITY SCORING (1.00 Operational / 0.00 Generic)',
      'ACTION USEFULNESS SCORE',
    ],
    whatItDoes:
      'Penalizes unhelpful generic deflections by -0.2 in the final rerank score, favoring concrete resolution precedents.',
    configuredWeight: 'Penalty Weight: -0.2 (configs/reranking.yaml)',
    limitation:
      'This is a rule-based operational heuristic signal, not a guarantee of agent response quality.',
  },
  action: {
    whatItMeans:
      'Boilerplate penalty evaluation. Historical brand responses containing deflection phrases receive a penalty (-0.2); specific operational responses receive full usefulness (1.00).',
    howWeCalculateIt:
      'Scans the historical Amazon brand response for generic deflection boilerplate patterns ("reach us via phone or chat", "send us a dm", "dm us", "click the link below"). If generic boilerplate is detected, an action penalty flag is set. Specific operational responses with resolution guidance receive full usefulness (1.00).',
    pipelineSteps: [
      'HISTORICAL AMAZON RESPONSE',
      'BOILERPLATE REGEX AUDIT (Deflection Detection)',
      'ACTIONABILITY SCORING (1.00 Operational / 0.00 Generic)',
      'ACTION USEFULNESS SCORE',
    ],
    whatItDoes:
      'Penalizes unhelpful generic deflections by -0.2 in the final rerank score, favoring concrete resolution precedents.',
    configuredWeight: 'Penalty Weight: -0.2 (configs/reranking.yaml)',
    limitation:
      'This is a rule-based operational heuristic signal, not a guarantee of agent response quality.',
  },
};

export const RankingSignal: React.FC<RankingSignalProps> = ({
  signal,
  currentIntent,
  currentStates,
}) => {
  const [expanded, setExpanded] = useState(false);

  // Normalize score to 0.xx decimal representation, or render N/A if uncomputed
  const isScoreAvailable = signal.score !== null && signal.score !== undefined;
  const numericScore = typeof signal.score === 'number' ? signal.score : 0;
  const decimalScore = numericScore <= 1.0 ? numericScore : numericScore / 100;
  const displayScore = isScoreAvailable ? decimalScore.toFixed(2) : 'N/A';
  const percentage = isScoreAvailable ? Math.min(Math.max(decimalScore * 100, 0), 100) : 0;

  const signalKey = signal.name.toLowerCase();
  const explanation =
    SIGNAL_EXPLANATIONS[signalKey] ||
    SIGNAL_EXPLANATIONS[signalKey.replace('_similarity', '').replace('_overlap', '')] ||
    SIGNAL_EXPLANATIONS.semantic;

  // Clean label names per requirement
  let displayLabel = signal.label;
  if (signalKey === 'intent') displayLabel = 'Intent Compatibility';
  if (signalKey === 'area') displayLabel = 'Area Compatibility';
  if (signalKey === 'lexical') displayLabel = 'Lexical Match';
  if (signalKey === 'semantic') displayLabel = 'Semantic Similarity';
  if (signalKey === 'state') displayLabel = 'State Compatibility';
  if (signalKey === 'action' || signalKey === 'action_usefulness') displayLabel = 'Action Usefulness';

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        padding: '8px 10px',
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-xs)',
        fontSize: '12px',
      }}
    >
      {/* Header Row */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ color: 'var(--ink)', fontWeight: 600, fontSize: '12px' }}>
            {displayLabel}
          </span>
          <span
            style={{
              fontSize: '9px',
              fontFamily: 'var(--font-mono)',
              textTransform: 'uppercase',
              color: 'var(--slate)',
              backgroundColor: '#f1f5f9',
              padding: '1px 5px',
              borderRadius: '2px',
              letterSpacing: '0.04em',
            }}
          >
            Reranking signal
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {signal.weight !== undefined && (
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '10px',
                color: 'var(--slate)',
                backgroundColor: '#f8fafc',
                padding: '1px 4px',
                borderRadius: '2px',
                border: '1px solid #e2e8f0',
              }}
              title="Configured weight in configs/reranking.yaml"
            >
              Weight: {signal.weight}
            </span>
          )}
          <span
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              fontWeight: 700,
              color: isScoreAvailable ? 'var(--cohere-black)' : 'var(--slate)',
            }}
            title={!isScoreAvailable ? 'Not computed for this candidate.' : undefined}
          >
            {displayScore}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div
        style={{
          height: '4px',
          width: '100%',
          backgroundColor: '#e2e8f0',
          borderRadius: 'var(--radius-full)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${percentage}%`,
            backgroundColor:
              decimalScore >= 0.8
                ? 'var(--deep-enterprise-green)'
                : decimalScore >= 0.5
                ? 'var(--ink)'
                : 'var(--slate)',
            borderRadius: 'var(--radius-full)',
            transition: 'width 300ms ease',
          }}
        />
      </div>

      {/* Interactive "How is this calculated?" Toggle */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginTop: '2px',
        }}
      >
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          title="What does this mean? Click to expand detailed calculation logic."
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            background: 'none',
            border: 'none',
            padding: '2px 0',
            cursor: 'pointer',
            fontFamily: 'var(--font-mono)',
            fontSize: '10px',
            color: 'var(--slate)',
            transition: 'color 150ms ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--deep-enterprise-green)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--slate)')}
        >
          <Info size={11} />
          <span>{expanded ? 'Hide calculation details' : 'How is this calculated?'}</span>
          {expanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
        </button>

        <span style={{ fontSize: '10px', color: 'var(--muted-slate)', fontFamily: 'var(--font-mono)' }}>
          {explanation.configuredWeight}
        </span>
      </div>

      {/* Expanded Explanation Card */}
      {expanded && (
        <div
          style={{
            marginTop: '6px',
            padding: '10px 12px',
            backgroundColor: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: 'var(--radius-xs)',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            fontFamily: 'var(--font-sans)',
            fontSize: '11px',
            lineHeight: 1.45,
          }}
        >
          {/* WHAT IT MEANS */}
          <div>
            <div
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '9px',
                fontWeight: 700,
                color: 'var(--slate)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                marginBottom: '2px',
              }}
            >
              WHAT IT MEANS
            </div>
            <div style={{ color: 'var(--ink)' }}>{explanation.whatItMeans}</div>
          </div>

          {/* HOW WE CALCULATE IT */}
          <div>
            <div
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '9px',
                fontWeight: 700,
                color: 'var(--slate)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                marginBottom: '2px',
              }}
            >
              HOW WE CALCULATE IT
            </div>
            <div style={{ color: 'var(--ink)' }}>{explanation.howWeCalculateIt}</div>
          </div>

          {/* Contextual Information if Available */}
          {signalKey === 'intent' && currentIntent && (
            <div
              style={{
                padding: '4px 8px',
                backgroundColor: '#ffffff',
                border: '1px solid #cbd5e1',
                borderRadius: '2px',
                fontFamily: 'var(--font-mono)',
                fontSize: '10px',
                color: 'var(--ink)',
              }}
            >
              <span style={{ color: 'var(--slate)' }}>Current Predicted Intent: </span>
              <strong>{currentIntent}</strong>
            </div>
          )}

          {signalKey === 'state' && currentStates && currentStates.length > 0 && (
            <div
              style={{
                padding: '4px 8px',
                backgroundColor: '#ffffff',
                border: '1px solid #cbd5e1',
                borderRadius: '2px',
                fontFamily: 'var(--font-mono)',
                fontSize: '10px',
                color: 'var(--ink)',
              }}
            >
              <span style={{ color: 'var(--slate)' }}>Current Operational State: </span>
              <strong>{currentStates.join(', ')}</strong>
            </div>
          )}

          {/* PIPELINE SIGNAL FLOW */}
          <div
            style={{
              padding: '6px 8px',
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '2px',
              fontFamily: 'var(--font-mono)',
              fontSize: '9px',
              display: 'flex',
              flexDirection: 'column',
              gap: '3px',
            }}
          >
            <div style={{ color: 'var(--slate)', fontWeight: 600 }}>SIGNAL COMPUTATION PIPELINE:</div>
            {explanation.pipelineSteps.map((step, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--ink)' }}>
                {idx > 0 && <ArrowRight size={9} color="var(--slate)" />}
                <span>{step}</span>
              </div>
            ))}
          </div>

          {/* WHAT IT DOES */}
          <div>
            <div
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '9px',
                fontWeight: 700,
                color: 'var(--slate)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                marginBottom: '2px',
              }}
            >
              WHAT IT DOES IN RERANKING
            </div>
            <div style={{ color: 'var(--ink)' }}>
              {explanation.whatItDoes} ({explanation.configuredWeight})
            </div>
          </div>

          {/* IMPORTANT LIMITATION */}
          <div
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '6px',
              padding: '6px 8px',
              backgroundColor: '#fffbeb',
              border: '1px solid #fef3c7',
              borderRadius: '2px',
              fontSize: '10px',
              color: '#92400e',
            }}
          >
            <AlertTriangle size={12} style={{ flexShrink: 0, marginTop: '1px' }} />
            <div>
              <strong>Important limitation:</strong> {explanation.limitation}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

