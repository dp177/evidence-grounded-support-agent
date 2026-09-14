import React, { useState } from 'react';
import { RetrievalEvidence, RerankingResult, ClassificationResult } from '../../types/agent';
import { Database, ChevronDown, ChevronUp, Layers, CheckCircle2 } from 'lucide-react';


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
                  RRF FUSION
                </span>
              </div>

              {/* Two-Ranking RRF Retrieval Summary */}
              {evidenceList.length > 0 && (
                <div
                  style={{
                    padding: '8px 10px',
                    backgroundColor: '#f8fafc',
                    border: '1px solid var(--border-light)',
                    borderRadius: 'var(--radius-xs)',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '10px',
                    color: 'var(--slate)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px',
                  }}
                >
                  <div style={{ fontWeight: 600, color: 'var(--ink)' }}>
                    FUSION FLOW:
                  </div>
                  <div>
                    30 semantic candidates + 30 lexical candidates → Reciprocal Rank Fusion (k=60) → Top {evidenceList.length} precedents
                  </div>
                  <div style={{ color: 'var(--deep-enterprise-green)', fontWeight: 600 }}>
                    RRF Formula: RRF(d) = 1/(60 + semantic_rank) + 1/(60 + lexical_rank)
                  </div>
                </div>
              )}


              {/* Why This Case Ranked High */}
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

                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px', color: 'var(--ink)' }}>
                    <CheckCircle2 size={12} color="var(--deep-enterprise-green)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>
                      <strong>Semantic position:</strong>{' '}
                      {evidenceList[0]?.semantic_rank !== null && evidenceList[0]?.semantic_rank !== undefined ? (
                        <>
                          Ranked <strong>#{evidenceList[0].semantic_rank}</strong> in dense semantic retrieval
                          {evidenceList[0].semantic_score !== null && evidenceList[0].semantic_score !== undefined
                            ? ` (cosine similarity: ${evidenceList[0].semantic_score.toFixed(2)})`
                            : ''}
                          , contributing <code>1/(60 + {evidenceList[0].semantic_rank}) = {(1.0 / (60 + evidenceList[0].semantic_rank)).toFixed(5)}</code>.
                        </>
                      ) : (
                        <>Did not appear in Top 30 dense semantic candidates (contributes 0.0).</>
                      )}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px', color: 'var(--ink)' }}>
                    <CheckCircle2 size={12} color="var(--deep-enterprise-green)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>
                      <strong>Lexical position:</strong>{' '}
                      {evidenceList[0]?.lexical_rank !== null && evidenceList[0]?.lexical_rank !== undefined ? (
                        <>
                          Ranked <strong>#{evidenceList[0].lexical_rank}</strong> in sparse lexical retrieval
                          {evidenceList[0].lexical_score !== null && evidenceList[0].lexical_score !== undefined
                            ? ` (TF-IDF overlap: ${evidenceList[0].lexical_score.toFixed(2)})`
                            : ''}
                          , contributing <code>1/(60 + {evidenceList[0].lexical_rank}) = {(1.0 / (60 + evidenceList[0].lexical_rank)).toFixed(5)}</code>.
                        </>
                      ) : (
                        <>Did not appear in Top 30 lexical candidates (contributes 0.0).</>
                      )}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px', color: 'var(--ink)' }}>
                    <CheckCircle2 size={12} color="var(--deep-enterprise-green)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>
                      <strong>Combined RRF score:</strong>{' '}
                      <strong style={{ color: 'var(--deep-enterprise-green)' }}>
                        {evidenceList[0]?.rrf_score !== null && evidenceList[0]?.rrf_score !== undefined
                          ? evidenceList[0].rrf_score.toFixed(5)
                          : (evidenceList[0]?.final_score !== null && evidenceList[0]?.final_score !== undefined ? evidenceList[0].final_score.toFixed(5) : '—')}
                      </strong>
                      . Fused using Reciprocal Rank Fusion (k=60) over semantic and lexical rankings.
                    </span>
                  </div>
                </div>
              </div>

              {/* Truthful Candidate Table: Rank | Case | Semantic Rank | Lexical Rank | RRF Score */}
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
                      <th style={{ padding: '6px 8px' }}>Semantic Rank</th>
                      <th style={{ padding: '6px 8px' }}>Lexical Rank</th>
                      <th style={{ padding: '6px 8px' }}>RRF Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {evidenceList.slice(0, 5).map((c, idx) => {
                      const rankNum = c.rank ?? idx + 1;
                      const rrfVal =
                        c.rrf_score !== null && c.rrf_score !== undefined
                          ? c.rrf_score.toFixed(5)
                          : (c.final_score !== null && c.final_score !== undefined ? c.final_score.toFixed(5) : '—');

                      return (
                        <tr key={c.case_id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                          <td style={{ padding: '6px 8px', fontWeight: 600 }}>#{rankNum}</td>
                          <td style={{ padding: '6px 8px', fontWeight: 600, color: 'var(--ink)' }}>{c.case_id}</td>
                          <td style={{ padding: '6px 8px' }}>
                            {c.semantic_rank !== null && c.semantic_rank !== undefined ? (
                              <span>
                                #{c.semantic_rank}{' '}
                                {c.semantic_score !== null && c.semantic_score !== undefined && (
                                  <span style={{ color: 'var(--slate)', fontSize: '9px' }}>
                                    (cos {c.semantic_score.toFixed(2)})
                                  </span>
                                )}
                              </span>
                            ) : (
                              <span style={{ color: 'var(--slate)' }}>—</span>
                            )}
                          </td>
                          <td style={{ padding: '6px 8px' }}>
                            {c.lexical_rank !== null && c.lexical_rank !== undefined ? (
                              <span>
                                #{c.lexical_rank}{' '}
                                {c.lexical_score !== null && c.lexical_score !== undefined && (
                                  <span style={{ color: 'var(--slate)', fontSize: '9px' }}>
                                    (tfidf {c.lexical_score.toFixed(2)})
                                  </span>
                                )}
                              </span>
                            ) : (
                              <span style={{ color: 'var(--slate)' }}>—</span>
                            )}
                          </td>
                          <td style={{ padding: '6px 8px', fontWeight: 700, color: 'var(--deep-enterprise-green)' }}>
                            {rrfVal}
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
                These scores are reciprocal rank fusion values (k=60) combining ordinal positions from semantic and lexical retrievers. They are ranking values, not calibrated probabilities.
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
