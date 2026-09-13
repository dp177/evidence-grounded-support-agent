import React, { useState } from 'react';
import { RetrievalEvidence, RerankingResult, ClassificationResult } from '../../types/agent';
import { Database, ChevronDown, ChevronUp, Layers } from 'lucide-react';
import { RankingSignal } from '../reranking/RankingSignal';
import { CheckCircle2 } from 'lucide-react';

interface InlineEvidenceProps {
  evidenceList: RetrievalEvidence[];
  reranking?: RerankingResult;
  classification?: ClassificationResult;
}

export const InlineEvidence: React.FC<InlineEvidenceProps> = ({
  evidenceList,
  reranking,
  classification,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [showReranking, setShowReranking] = useState(false);

  if (!evidenceList || evidenceList.length === 0) return null;

  return (
    <div
      style={{
        borderRadius: 'var(--radius-xs)',
        border: '1px solid var(--border-light)',
        backgroundColor: '#ffffff',
        overflow: 'hidden',
        fontSize: '12px',
        margin: 'var(--space-6) 0',
      }}
    >
      {/* Evidence Bar */}
      <div
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '6px 12px',
          background: '#f8fafc',
          borderBottom: expanded ? '1px solid var(--border-light)' : 'none',
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
        }}
      >
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: 0,
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
          }}
        >
          <Database size={12} color="var(--deep-enterprise-green)" />
          <span
            style={{
              backgroundColor: 'var(--near-black-primary)',
              color: '#ffffff',
              padding: '1px 5px',
              borderRadius: '2px',
              fontSize: '9px',
              fontWeight: 600,
              letterSpacing: '0.3px',
            }}
          >
            HISTORICAL PRECEDENT
          </span>
          <strong style={{ color: 'var(--ink)' }}>
            {evidenceList.length} precedents cited
          </strong>
          <span style={{ color: 'var(--slate)', display: 'flex', alignItems: 'center', gap: '2px' }}>
            {expanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
          </span>
        </button>

        {/* Expandable "Why these cases?" trigger */}
        <button
          type="button"
          onClick={() => setShowReranking(!showReranking)}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: 'var(--action-blue)',
            fontFamily: 'var(--font-mono)',
            fontSize: '10px',
            display: 'flex',
            alignItems: 'center',
            gap: '3px',
            padding: '2px 6px',
            borderRadius: 'var(--radius-xs)',
          }}
        >
          <Layers size={10} />
          <span>{showReranking ? 'Hide ranking signals' : 'Why these cases?'}</span>
        </button>
      </div>

      {/* "Why these cases?" Reranking explanation panel */}
      {showReranking && (
        <div
          style={{
            padding: '12px 14px',
            backgroundColor: '#f8fafc',
            borderBottom: '1px solid var(--border-light)',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }}
        >
          {reranking ? (
            <>
              {/* Funnel Overview */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  color: 'var(--ink)',
                  borderBottom: '1px solid #e2e8f0',
                  paddingBottom: '8px',
                }}
              >
                <div>
                  <strong>Multi-Stage Reranker Funnel:</strong>{' '}
                  <span style={{ color: 'var(--slate)' }}>
                    {reranking.candidate_count} candidates → {reranking.final_count} selected ({reranking.unique_conversations} threads)
                  </span>
                </div>
                <span
                  style={{
                    fontSize: '9px',
                    backgroundColor: '#e2e8f0',
                    color: 'var(--slate)',
                    padding: '1px 6px',
                    borderRadius: '2px',
                  }}
                >
                  FEATURE SCORING
                </span>
              </div>

              {/* Selected Candidate Compatibility Signals */}
              {evidenceList.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span className="mono-label" style={{ fontSize: '10px' }}>
                      SELECTED CANDIDATE SIGNALS (Rank #{evidenceList[0]?.rank || 1}: {evidenceList[0]?.case_id})
                    </span>
                    <span style={{ fontSize: '10px', color: 'var(--slate)', fontFamily: 'var(--font-mono)' }}>
                      Per-candidate feature scores
                    </span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {[
                      {
                        name: 'semantic',
                        label: 'Semantic Similarity',
                        score: evidenceList[0]?.semantic_score !== null && evidenceList[0]?.semantic_score !== undefined
                          ? evidenceList[0].semantic_score
                          : (evidenceList[0]?.similarity ?? null),
                        weight: reranking.weights?.semantic ?? 1.0,
                      },
                      {
                        name: 'lexical',
                        label: 'Lexical Match',
                        score: evidenceList[0]?.lexical_score ?? null,
                        weight: reranking.weights?.lexical ?? 0.3,
                      },
                      {
                        name: 'intent',
                        label: 'Intent Compatibility',
                        score: evidenceList[0]?.intent_score ?? null,
                        weight: reranking.weights?.intent ?? 0.2,
                      },
                      {
                        name: 'state',
                        label: 'State Compatibility',
                        score: evidenceList[0]?.state_score ?? null,
                        weight: reranking.weights?.state ?? 0.1,
                      },
                      {
                        name: 'action_usefulness',
                        label: 'Action Usefulness',
                        score: evidenceList[0]?.action_usefulness ?? null,
                        weight: reranking.weights?.action_penalty ?? -0.2,
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
              )}

              {/* Why This Case Was Selected Checklist */}
              <div
                style={{
                  padding: '10px 12px',
                  backgroundColor: '#ffffff',
                  border: '1px solid var(--border-light)',
                  borderRadius: 'var(--radius-xs)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                  fontSize: '11px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span className="mono-label" style={{ fontSize: '10px' }}>
                    WHY THIS CASE RANKED HIGH ({evidenceList[0]?.case_id || 'Rank #1'})
                  </span>
                  <span style={{ fontSize: '9px', color: 'var(--slate)', fontFamily: 'var(--font-mono)' }}>
                    Rank #{evidenceList[0]?.rank || 1} Precedent
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--ink)' }}>
                    <CheckCircle2 size={12} color="var(--deep-enterprise-green)" style={{ flexShrink: 0 }} />
                    <span>
                      <strong>Semantic similarity ({evidenceList[0]?.semantic_score !== null && evidenceList[0]?.semantic_score !== undefined ? evidenceList[0].semantic_score.toFixed(2) : (evidenceList[0]?.similarity ? evidenceList[0].similarity.toFixed(2) : 'N/A')}):</strong> Cosine similarity between current retrieval query embedding and this historical document embedding.
                    </span>
                  </div>

                  {evidenceList[0]?.lexical_score !== null && evidenceList[0]?.lexical_score !== undefined && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--ink)' }}>
                      <CheckCircle2 size={12} color="var(--deep-enterprise-green)" style={{ flexShrink: 0 }} />
                      <span>
                        <strong>Lexical match ({evidenceList[0].lexical_score.toFixed(2)}):</strong> TF-IDF vocabulary overlap between query and customer message.
                      </span>
                    </div>
                  )}

                  {evidenceList[0]?.action_usefulness !== null && evidenceList[0]?.action_usefulness !== undefined && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--ink)' }}>
                      <CheckCircle2 size={12} color="var(--deep-enterprise-green)" style={{ flexShrink: 0 }} />
                      <span>
                        <strong>Action usefulness ({evidenceList[0].action_usefulness.toFixed(2)}):</strong> {evidenceList[0].action_usefulness >= 1.0 ? 'Historical brand response provides operational resolution guidance without deflection boilerplate.' : 'Action penalty applied for boilerplate deflection.'}
                      </span>
                    </div>
                  )}

                  {evidenceList[0]?.intent_score !== null && evidenceList[0]?.intent_score !== undefined ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--ink)' }}>
                      <CheckCircle2 size={12} color="var(--deep-enterprise-green)" style={{ flexShrink: 0 }} />
                      <span>
                        <strong>Intent compatibility ({evidenceList[0].intent_score.toFixed(2)}):</strong> Compatibility signal between current predicted intent and candidate.
                      </span>
                    </div>
                  ) : null}

                  {evidenceList[0]?.state_score !== null && evidenceList[0]?.state_score !== undefined ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--ink)' }}>
                      <CheckCircle2 size={12} color="var(--deep-enterprise-green)" style={{ flexShrink: 0 }} />
                      <span>
                        <strong>State compatibility ({evidenceList[0].state_score.toFixed(2)}):</strong> Inferred compatibility signal with current conversation state.
                      </span>
                    </div>
                  ) : null}

                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--ink)' }}>
                    <CheckCircle2 size={12} color="var(--deep-enterprise-green)" style={{ flexShrink: 0 }} />
                    <span>
                      <strong>Final rerank score ({evidenceList[0]?.rerank_score !== null && evidenceList[0]?.rerank_score !== undefined ? evidenceList[0].rerank_score.toFixed(3) : (evidenceList[0]?.final_score !== null && evidenceList[0]?.final_score !== undefined ? evidenceList[0].final_score.toFixed(3) : 'N/A')}):</strong> Weighted multi-signal rank score.
                    </span>
                  </div>

                  {(evidenceList[0]?.intent_score === null || evidenceList[0]?.intent_score === undefined || evidenceList[0]?.state_score === null || evidenceList[0]?.state_score === undefined) && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--slate)', fontSize: '10px', marginTop: '2px' }}>
                      <span>
                        ℹ Additional compatibility signals (Intent &amp; State) were not computed for this candidate (historical cases lack metadata labels).
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Truthful Candidate Table: Rank | Case | Semantic | Lexical | Intent | State | Action | Final */}
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
                    <tr style={{ backgroundColor: '#f1f5f9', borderBottom: '1px solid var(--border-light)' }}>
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
                    {evidenceList.slice(0, 5).map((c, idx) => {
                      const rankNum = c.rank ?? idx + 1;
                      return (
                        <tr key={c.case_id} style={{ borderBottom: '1px solid #f1f5f9' }}>
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
                    })}
                  </tbody>
                </table>
              </div>

              {/* Required Honesty / Limitation Notice */}
              <div
                style={{
                  fontSize: '10px',
                  color: 'var(--slate)',
                  fontStyle: 'italic',
                  lineHeight: 1.4,
                  borderTop: '1px solid #e2e8f0',
                  paddingTop: '6px',
                }}
              >
                These scores are ranking signals used to order historical evidence. They are not calibrated probabilities or human-labelled historical ground truth.
              </div>
            </>
          ) : (
            <div style={{ color: 'var(--slate)', fontStyle: 'italic', fontSize: '10px' }}>
              Detailed ranking information unavailable
            </div>
          )}
        </div>
      )}

      {/* Precedents List */}
      {expanded && (
        <div
          style={{
            padding: '10px 14px',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            backgroundColor: '#fafafb',
          }}
        >
          {evidenceList.slice(0, 5).map((ev) => (
            <div
              key={ev.case_id}
              style={{
                padding: '10px 12px',
                borderRadius: 'var(--radius-xs)',
                backgroundColor: '#ffffff',
                border: '1px solid var(--card-border)',
                display: 'flex',
                flexDirection: 'column',
                gap: '5px',
                fontSize: '11px',
              }}
            >
              {/* Header: HISTORICAL PRECEDENT + Case ID + Similarity */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span
                    style={{
                      backgroundColor: 'var(--near-black-primary)',
                      color: '#ffffff',
                      padding: '1px 5px',
                      borderRadius: '2px',
                      fontSize: '9px',
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 600,
                    }}
                  >
                    HISTORICAL PRECEDENT
                  </span>
                  <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--slate)', fontSize: '10px' }}>
                    Case ID: <strong>{ev.case_id}</strong>
                  </span>
                </div>

                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--action-blue)', fontWeight: 600 }}>
                  Similarity: {ev.similarity.toFixed(2)}
                </span>
              </div>

              {/* Customer Statement */}
              <div style={{ color: 'var(--slate)', fontSize: '11px', lineHeight: '1.4' }}>
                <strong style={{ color: 'var(--ink)' }}>Customer:</strong> "{ev.customer_message}"
              </div>

              {/* Relevant Context */}
              {ev.relevant_context && (
                <div style={{ color: 'var(--slate)', fontSize: '11px', lineHeight: '1.4' }}>
                  <strong style={{ color: 'var(--ink)' }}>Relevant context:</strong> {ev.relevant_context}
                </div>
              )}

              {/* Amazon Response */}
              <div
                style={{
                  color: 'var(--deep-enterprise-green)',
                  fontSize: '11px',
                  lineHeight: '1.4',
                  backgroundColor: 'var(--pale-green-wash)',
                  padding: '5px 8px',
                  borderRadius: '2px',
                  marginTop: '2px',
                }}
              >
                <strong>Amazon response:</strong> {ev.brand_response}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
