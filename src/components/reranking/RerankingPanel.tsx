import React, { useState } from 'react';
import { RerankingResult, ClassificationResult, RetrievalEvidence } from '../../types/agent';
import { RankingSignal } from './RankingSignal';
import { CandidateList } from './CandidateList';
import {
  Sparkles,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Sliders,
  Calculator,
  Terminal,
  AlertCircle,
  HelpCircle,
  ArrowRight,
} from 'lucide-react';

interface RerankingPanelProps {
  reranking?: RerankingResult | null;
  classification?: ClassificationResult | null;
  selectedCaseId?: string;
  retrievedEvidence?: RetrievalEvidence[];
}

export const RerankingPanel: React.FC<RerankingPanelProps> = ({
  reranking,
  classification,
  selectedCaseId,
  retrievedEvidence,
}) => {
  const [showFormula, setShowFormula] = useState(false);
  const [showWeights, setShowWeights] = useState(false);
  const [showTechnicalScoring, setShowTechnicalScoring] = useState(false);

  if (!reranking) {
    return null;
  }

  // Active or top candidate for "Why this case was selected"
  const rankedCases: RetrievalEvidence[] =
    (reranking.ranked_cases && reranking.ranked_cases.length > 0)
      ? reranking.ranked_cases
      : (retrievedEvidence || []);
  const topCandidate =
    rankedCases.find((c) => c.case_id === selectedCaseId) || rankedCases[0];

  // Default weights from configs/reranking.yaml
  const weights = reranking.weights || {
    semantic: 1.0,
    lexical: 0.3,
    intent: 0.2,
    area: 0.1,
    state: 0.1,
    action_penalty: -0.2,
  };

  const primaryIntent = classification?.primary_intent || 'Identified Category';
  const statesList = classification?.states || ['INITIAL_INQUIRY'];

  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-sm)',
        padding: 'var(--space-16)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-14)',
      }}
    >
      {/* 1. Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--card-border)',
          paddingBottom: 'var(--space-8)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
          <Sparkles size={14} color="var(--deep-enterprise-green)" />
          <h3
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '13px',
              fontWeight: 600,
              color: 'var(--cohere-black)',
            }}
          >
            Why these cases?
          </h3>
        </div>

        <span className="mono-label" style={{ fontSize: '10px' }}>
          MULTI-STAGE RERANKER
        </span>
      </div>

      {/* 2. Candidate Funnel */}
      <CandidateList
        candidateCount={reranking.candidate_count}
        finalCount={reranking.final_count}
        uniqueConversations={reranking.unique_conversations}
      />

      {/* 3. Signals Breakdown: Selected Candidate Signals */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span className="mono-label" style={{ fontSize: '10px' }}>
            SELECTED CANDIDATE SIGNALS ({topCandidate ? `Rank #${topCandidate.rank || 1}: ${topCandidate.case_id}` : 'None'})
          </span>
          <span style={{ fontSize: '10px', color: 'var(--slate)', fontFamily: 'var(--font-mono)' }}>
            Per-candidate feature scores
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          {[
            {
              name: 'semantic',
              label: 'Semantic Similarity',
              score: topCandidate?.semantic_score !== null && topCandidate?.semantic_score !== undefined
                ? topCandidate.semantic_score
                : (topCandidate?.similarity ?? null),
              weight: weights.semantic ?? 1.0,
            },
            {
              name: 'lexical',
              label: 'Lexical Match',
              score: topCandidate?.lexical_score ?? null,
              weight: weights.lexical ?? 0.3,
            },
            {
              name: 'intent',
              label: 'Intent Compatibility',
              score: topCandidate?.intent_score ?? null,
              weight: weights.intent ?? 0.2,
            },
            {
              name: 'state',
              label: 'State Compatibility',
              score: topCandidate?.state_score ?? null,
              weight: weights.state ?? 0.1,
            },
            {
              name: 'action_usefulness',
              label: 'Action Usefulness',
              score: topCandidate?.action_usefulness ?? null,
              weight: weights.action_penalty ?? -0.2,
            },
          ].map((sig) => (
            <RankingSignal
              key={sig.name}
              signal={sig}
              currentIntent={classification?.primary_intent}
              currentStates={classification?.states}
            />
          ))}
        </div>
      </div>

      {/* 4. FINAL RERANKING Funnel & Explanation */}
      <div
        style={{
          padding: '10px 12px',
          backgroundColor: '#f8fafc',
          border: '1px solid var(--border-light)',
          borderRadius: 'var(--radius-xs)',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          fontSize: '11px',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontFamily: 'var(--font-mono)',
            fontSize: '10px',
            color: 'var(--ink)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <strong>FINAL RERANKING FUNNEL:</strong>
          </div>
          <button
            type="button"
            onClick={() => setShowFormula(!showFormula)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '3px',
              background: 'none',
              border: 'none',
              color: 'var(--deep-enterprise-green)',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            <Calculator size={11} />
            <span>{showFormula ? 'Hide formula' : 'How did this case rank?'}</span>
            {showFormula ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
          </button>
        </div>

        {/* Funnel flow diagram */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontFamily: 'var(--font-mono)',
            fontSize: '10px',
            color: 'var(--slate)',
            flexWrap: 'wrap',
          }}
        >
          <span>30 candidates</span>
          <ArrowRight size={10} />
          <span>5 scoring signals</span>
          <ArrowRight size={10} />
          <span>final rerank score</span>
          <ArrowRight size={10} />
          <strong style={{ color: 'var(--deep-enterprise-green)' }}>Top 5 evidence</strong>
        </div>

        {/* Expandable "How did this case rank?" Formula */}
        {showFormula && (
          <div
            style={{
              padding: '8px 10px',
              backgroundColor: '#ffffff',
              border: '1px solid #cbd5e1',
              borderRadius: '2px',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
              fontFamily: 'var(--font-mono)',
              fontSize: '10px',
              color: 'var(--ink)',
            }}
          >
            <div style={{ fontWeight: 600, color: 'var(--slate)' }}>
              FORMULA (configs/reranking.yaml):
            </div>
            <div style={{ backgroundColor: '#f1f5f9', padding: '6px', borderRadius: '2px', lineHeight: 1.5 }}>
              Final Score = (1.0 × Semantic) + (0.3 × Lexical) + (0.2 × Intent) + (0.1 × Area) + (0.1 × State) - (0.2 × Action Penalty)
            </div>
            <div style={{ color: 'var(--slate)', fontSize: '9px', fontStyle: 'italic' }}>
              Final score combines these signals using the configured reranking weights. Uncomputed features contribute 0.0 without faking zero scores.
            </div>
          </div>
        )}

        {/* Expandable "Scoring weights" */}
        <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '6px' }}>
          <button
            type="button"
            onClick={() => setShowWeights(!showWeights)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontFamily: 'var(--font-mono)',
              fontSize: '10px',
              color: 'var(--slate)',
            }}
          >
            <Sliders size={11} />
            <span>{showWeights ? 'Hide configuration weights' : 'Reranking Configuration Weights (configs/reranking.yaml)'}</span>
            {showWeights ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
          </button>

          {showWeights && (
            <div
              style={{
                marginTop: '6px',
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '4px 12px',
                fontFamily: 'var(--font-mono)',
                fontSize: '10px',
                padding: '6px 8px',
                backgroundColor: '#ffffff',
                border: '1px solid #cbd5e1',
                borderRadius: '2px',
              }}
            >
              <div>Semantic Weight: <strong>{weights.semantic ?? 1.0}</strong></div>
              <div>Lexical Weight: <strong>{weights.lexical ?? 0.3}</strong></div>
              <div>Intent Weight: <strong>{weights.intent ?? 0.2}</strong></div>
              <div>Area Weight: <strong>{weights.area ?? 0.1}</strong></div>
              <div>State Weight: <strong>{weights.state ?? 0.1}</strong></div>
              <div>Action Penalty: <strong>{weights.action_penalty ?? -0.2}</strong></div>
            </div>
          )}
        </div>
      </div>

      {/* 5. Candidate Table: Truthful Per-Candidate Breakdown */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span className="mono-label" style={{ fontSize: '10px' }}>
            CANDIDATE RERANKING BREAKDOWN
          </span>
          <span style={{ fontSize: '10px', color: 'var(--slate)', fontFamily: 'var(--font-mono)' }}>
            Top {Math.min(rankedCases.length, 5)} Candidates
          </span>
        </div>

        <div
          style={{
            overflowX: 'auto',
            border: '1px solid var(--border-light)',
            borderRadius: 'var(--radius-xs)',
            fontSize: '10px',
            fontFamily: 'var(--font-mono)',
            backgroundColor: '#ffffff',
          }}
        >
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid var(--border-light)' }}>
                <th style={{ padding: '6px 8px' }}>Rank</th>
                <th style={{ padding: '6px 8px' }}>Case</th>
                <th style={{ padding: '6px 8px' }}>Semantic</th>
                <th style={{ padding: '6px 8px' }}>Lexical</th>
                <th style={{ padding: '6px 8px' }}>Intent</th>
                <th style={{ padding: '6px 8px' }}>State</th>
                <th style={{ padding: '6px 8px' }}>Action</th>
                <th style={{ padding: '6px 8px' }}>Final</th>
              </tr>
            </thead>
            <tbody>
              {rankedCases.length > 0 ? (
                rankedCases.slice(0, 5).map((c, idx) => {
                  const rankNum = c.rank ?? idx + 1;
                  const isSelected = c.case_id === topCandidate?.case_id;
                  return (
                    <tr
                      key={c.case_id}
                      style={{
                        borderBottom: '1px solid #f1f5f9',
                        backgroundColor: isSelected ? 'rgba(16, 185, 129, 0.05)' : undefined,
                      }}
                    >
                      <td style={{ padding: '6px 8px', fontWeight: 600 }}>#{rankNum}</td>
                      <td style={{ padding: '6px 8px', fontWeight: 600, color: 'var(--ink)' }}>{c.case_id}</td>
                      <td style={{ padding: '6px 8px' }}>
                        {c.semantic_score !== null && c.semantic_score !== undefined
                          ? c.semantic_score.toFixed(2)
                          : (c.similarity ? c.similarity.toFixed(2) : <span title="Not computed for this candidate." style={{ color: 'var(--slate)' }}>N/A</span>)}
                      </td>
                      <td style={{ padding: '6px 8px' }}>
                        {c.lexical_score !== null && c.lexical_score !== undefined
                          ? c.lexical_score.toFixed(2)
                          : <span title="Not computed for this candidate." style={{ color: 'var(--slate)' }}>N/A</span>}
                      </td>
                      <td style={{ padding: '6px 8px' }}>
                        {c.intent_score !== null && c.intent_score !== undefined
                          ? c.intent_score.toFixed(2)
                          : <span title="Not computed for this candidate." style={{ color: 'var(--slate)' }}>N/A</span>}
                      </td>
                      <td style={{ padding: '6px 8px' }}>
                        {c.state_score !== null && c.state_score !== undefined
                          ? c.state_score.toFixed(2)
                          : <span title="Not computed for this candidate." style={{ color: 'var(--slate)' }}>N/A</span>}
                      </td>
                      <td style={{ padding: '6px 8px' }}>
                        {c.action_usefulness !== null && c.action_usefulness !== undefined
                          ? c.action_usefulness.toFixed(2)
                          : <span title="Not computed for this candidate." style={{ color: 'var(--slate)' }}>N/A</span>}
                      </td>
                      <td style={{ padding: '6px 8px', fontWeight: 700, color: 'var(--deep-enterprise-green)' }}>
                        {c.rerank_score !== null && c.rerank_score !== undefined
                          ? c.rerank_score.toFixed(3)
                          : (c.final_score !== null && c.final_score !== undefined ? c.final_score.toFixed(3) : <span title="Not computed for this candidate." style={{ color: 'var(--slate)' }}>N/A</span>)}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={8} style={{ padding: '8px', textAlign: 'center', color: 'var(--slate)' }}>
                    No candidate scoring breakdown available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 6. "WHY THIS CASE WAS SELECTED" View: Fact-based only */}
      <div
        style={{
          padding: '10px 12px',
          backgroundColor: '#ffffff',
          border: '1px solid var(--border-light)',
          borderRadius: 'var(--radius-xs)',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span className="mono-label" style={{ fontSize: '10px' }}>
            WHY THIS CASE WAS SELECTED {topCandidate ? `(${topCandidate.case_id})` : ''}
          </span>
          <span style={{ fontSize: '9px', color: 'var(--slate)', fontFamily: 'var(--font-mono)' }}>
            Rank #{topCandidate?.rank || 1} Precedent
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', fontSize: '11px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--ink)' }}>
            <CheckCircle2 size={13} color="var(--deep-enterprise-green)" style={{ flexShrink: 0 }} />
            <span>
              <strong>Semantic similarity ({topCandidate?.semantic_score !== null && topCandidate?.semantic_score !== undefined ? topCandidate.semantic_score.toFixed(2) : (topCandidate?.similarity ? topCandidate.similarity.toFixed(2) : 'N/A')}):</strong> Cosine similarity between the current retrieval query embedding and this historical document embedding.
            </span>
          </div>

          {topCandidate?.lexical_score !== null && topCandidate?.lexical_score !== undefined && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--ink)' }}>
              <CheckCircle2 size={13} color="var(--deep-enterprise-green)" style={{ flexShrink: 0 }} />
              <span>
                <strong>Lexical match ({topCandidate.lexical_score.toFixed(2)}):</strong> TF-IDF vocabulary overlap between query and customer message.
              </span>
            </div>
          )}

          {topCandidate?.action_usefulness !== null && topCandidate?.action_usefulness !== undefined && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--ink)' }}>
              <CheckCircle2 size={13} color="var(--deep-enterprise-green)" style={{ flexShrink: 0 }} />
              <span>
                <strong>Action usefulness ({topCandidate.action_usefulness.toFixed(2)}):</strong> {topCandidate.action_usefulness >= 1.0 ? 'Historical brand response provides operational resolution guidance without deflection boilerplate.' : 'Action penalty applied for boilerplate deflection.'}
              </span>
            </div>
          )}

          {topCandidate?.intent_score !== null && topCandidate?.intent_score !== undefined ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--ink)' }}>
              <CheckCircle2 size={13} color="var(--deep-enterprise-green)" style={{ flexShrink: 0 }} />
              <span>
                <strong>Intent compatibility ({topCandidate.intent_score.toFixed(2)}):</strong> Compatibility signal between current predicted intent and historical candidate.
              </span>
            </div>
          ) : null}

          {topCandidate?.state_score !== null && topCandidate?.state_score !== undefined ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--ink)' }}>
              <CheckCircle2 size={13} color="var(--deep-enterprise-green)" style={{ flexShrink: 0 }} />
              <span>
                <strong>State compatibility ({topCandidate.state_score.toFixed(2)}):</strong> Inferred compatibility signal with current conversation state.
              </span>
            </div>
          ) : null}

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--ink)' }}>
            <CheckCircle2 size={13} color="var(--deep-enterprise-green)" style={{ flexShrink: 0 }} />
            <span>
              <strong>Final rerank score ({topCandidate?.rerank_score !== null && topCandidate?.rerank_score !== undefined ? topCandidate.rerank_score.toFixed(3) : (topCandidate?.final_score !== null && topCandidate?.final_score !== undefined ? topCandidate.final_score.toFixed(3) : 'N/A')}):</strong> Weighted multi-signal reranking score.
            </span>
          </div>

          {(topCandidate?.intent_score === null || topCandidate?.intent_score === undefined || topCandidate?.state_score === null || topCandidate?.state_score === undefined) && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--slate)', fontSize: '10px', marginTop: '2px' }}>
              <HelpCircle size={12} color="var(--slate)" style={{ flexShrink: 0 }} />
              <span>
                Additional compatibility signals were not computed for this candidate (historical corpus documents do not contain human-verified intent/state labels).
              </span>
            </div>
          )}
        </div>
      </div>

      {/* 7. REQUIRED HONESTY / LIMITATION FOOTER */}
      <div
        style={{
          borderTop: '1px solid var(--card-border)',
          paddingTop: 'var(--space-8)',
          fontSize: '10px',
          color: 'var(--slate)',
          lineHeight: 1.4,
          fontStyle: 'italic',
        }}
      >
        These scores are ranking signals used to order historical evidence. They are not calibrated probabilities or human-labelled historical ground truth.
      </div>
    </div>
  );
};

