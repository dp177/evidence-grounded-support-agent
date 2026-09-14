import React, { useState } from 'react';
import { RerankingResult, ClassificationResult, RetrievalEvidence } from '../../types/agent';
import { CandidateList } from './CandidateList';
import {
  Sparkles,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Calculator,
  ArrowRight,
  Database,
  Search,
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

  if (!reranking) {
    return null;
  }

  // Active or top candidate for "Why this case ranked high"
  const rankedCases: RetrievalEvidence[] =
    (reranking.ranked_cases && reranking.ranked_cases.length > 0)
      ? reranking.ranked_cases
      : (retrievedEvidence || []);
  const topCandidate =
    rankedCases.find((c) => c.case_id === selectedCaseId) || rankedCases[0];

  const k = reranking.k || 60;
  const semCandidatesCount = reranking.semantic_candidate_count ?? 30;
  const lexCandidatesCount = reranking.lexical_candidate_count ?? 30;

  // Helper to calculate individual reciprocal rank component
  const calcReciprocal = (rank?: number | null) => {
    if (rank && rank > 0) {
      return (1.0 / (k + rank)).toFixed(5);
    }
    return '0.00000';
  };

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
          RRF RERANKER
        </span>
      </div>

      {/* 2. Candidate Funnel & Flow */}
      <div
        style={{
          padding: '10px 12px',
          backgroundColor: '#f8fafc',
          border: '1px solid var(--border-light)',
          borderRadius: 'var(--radius-xs)',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
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
          <span style={{ fontWeight: 600, color: 'var(--slate)' }}>
            RETRIEVAL &amp; FUSION PIPELINE:
          </span>
          <button
            type="button"
            onClick={() => setShowFormula(!showFormula)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              background: 'none',
              border: 'none',
              color: 'var(--deep-enterprise-green)',
              cursor: 'pointer',
              fontWeight: 600,
              fontFamily: 'var(--font-mono)',
              fontSize: '10px',
            }}
          >
            <Calculator size={11} />
            <span>{showFormula ? 'Hide formula' : 'RRF Formula & Math'}</span>
            {showFormula ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
          </button>
        </div>

        {/* Required flow: 30 semantic candidates + 30 lexical candidates ↓ Reciprocal Rank Fusion ↓ Top 5 historical precedents */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            color: 'var(--slate)',
            flexWrap: 'wrap',
          }}
        >
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
            <Database size={11} color="var(--deep-enterprise-green)" />
            <strong>{semCandidatesCount} semantic candidates</strong>
          </span>
          <span>+</span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
            <Search size={11} color="var(--accent-blue, #2563eb)" />
            <strong>{lexCandidatesCount} lexical candidates</strong>
          </span>
          <ArrowRight size={11} />
          <span style={{ color: 'var(--ink)', fontWeight: 600 }}>Reciprocal Rank Fusion</span>
          <ArrowRight size={11} />
          <strong style={{ color: 'var(--deep-enterprise-green)' }}>
            Top {rankedCases.length} historical precedents
          </strong>
        </div>

        {/* Expandable RRF Formula Card */}
        {showFormula && (
          <div
            style={{
              marginTop: '4px',
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
              RECIPROCAL RANK FUSION FORMULA (k = {k}):
            </div>
            <div
              style={{
                backgroundColor: '#f1f5f9',
                padding: '8px',
                borderRadius: '2px',
                lineHeight: 1.6,
                fontWeight: 600,
                color: 'var(--cohere-black)',
              }}
            >
              RRF(d) = 1 / (60 + semantic_rank(d)) + 1 / (60 + lexical_rank(d))
            </div>
            <div style={{ color: 'var(--slate)', fontSize: '9px', lineHeight: 1.4 }}>
              • Ranks are 1-based (1 ≤ rank ≤ 30).<br />
              • If a candidate does not appear in one ranking, that ranking contributes 0.0 to its RRF score.<br />
              • Final ranking is determined strictly by descending RRF score, ensuring candidates matching both dense semantics and exact keyword intent rank highest.
            </div>

            {topCandidate && (
              <div
                style={{
                  marginTop: '4px',
                  padding: '6px 8px',
                  backgroundColor: '#ecfdf5',
                  border: '1px solid #a7f3d0',
                  borderRadius: '2px',
                  fontSize: '9.5px',
                  color: '#065f46',
                }}
              >
                <strong>Calculation for {topCandidate.case_id} (Rank #{topCandidate.rank || 1}):</strong><br />
                {topCandidate.semantic_rank ? `1/(60 + ${topCandidate.semantic_rank})` : '0.0 (unranked)'} +{' '}
                {topCandidate.lexical_rank ? `1/(60 + ${topCandidate.lexical_rank})` : '0.0 (unranked)'} ={' '}
                <strong>
                  {topCandidate.rrf_score !== null && topCandidate.rrf_score !== undefined
                    ? topCandidate.rrf_score.toFixed(5)
                    : (
                        (topCandidate.semantic_rank ? 1.0 / (k + topCandidate.semantic_rank) : 0) +
                        (topCandidate.lexical_rank ? 1.0 / (k + topCandidate.lexical_rank) : 0)
                      ).toFixed(5)}
                </strong>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 3. Candidate Table: Rank | Case | Semantic Rank | Lexical Rank | RRF Score */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span className="mono-label" style={{ fontSize: '10px' }}>
            RRF CANDIDATE RANKING TABLE
          </span>
          <span style={{ fontSize: '10px', color: 'var(--slate)', fontFamily: 'var(--font-mono)' }}>
            Top {Math.min(rankedCases.length, 5)} Selected Precedents
          </span>
        </div>

        <div
          style={{
            overflowX: 'auto',
            border: '1px solid var(--border-light)',
            borderRadius: 'var(--radius-xs)',
            fontSize: '11px',
            fontFamily: 'var(--font-mono)',
            backgroundColor: '#ffffff',
          }}
        >
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid var(--border-light)' }}>
                <th style={{ padding: '6px 8px' }}>Rank</th>
                <th style={{ padding: '6px 8px' }}>Case</th>
                <th style={{ padding: '6px 8px' }}>Semantic Rank</th>
                <th style={{ padding: '6px 8px' }}>Lexical Rank</th>
                <th style={{ padding: '6px 8px' }}>RRF Score</th>
              </tr>
            </thead>
            <tbody>
              {rankedCases.length > 0 ? (
                rankedCases.slice(0, 5).map((c, idx) => {
                  const rankNum = c.rank ?? idx + 1;
                  const isSelected = c.case_id === topCandidate?.case_id;
                  const rrfVal =
                    c.rrf_score !== null && c.rrf_score !== undefined
                      ? c.rrf_score.toFixed(5)
                      : (c.final_score !== null && c.final_score !== undefined ? c.final_score.toFixed(5) : '—');

                  return (
                    <tr
                      key={c.case_id}
                      style={{
                        borderBottom: '1px solid #f1f5f9',
                        backgroundColor: isSelected ? 'rgba(16, 185, 129, 0.05)' : undefined,
                      }}
                    >
                      <td style={{ padding: '6px 8px', fontWeight: 600 }}>#{rankNum}</td>
                      <td style={{ padding: '6px 8px', fontWeight: 600, color: 'var(--ink)' }}>
                        {c.case_id}
                      </td>
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
                      <td
                        style={{
                          padding: '6px 8px',
                          fontWeight: 700,
                          color: 'var(--deep-enterprise-green)',
                        }}
                      >
                        {rrfVal}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={5} style={{ padding: '8px', textAlign: 'center', color: 'var(--slate)' }}>
                    No candidates available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. "WHY THIS CASE RANKED HIGH": Semantic position, Lexical position, Combined RRF score */}
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
            WHY THIS CASE RANKED HIGH {topCandidate ? `(${topCandidate.case_id})` : ''}
          </span>
          <span style={{ fontSize: '9px', color: 'var(--slate)', fontFamily: 'var(--font-mono)' }}>
            Rank #{topCandidate?.rank || 1} Precedent
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '11px' }}>
          {/* Position in semantic */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px', color: 'var(--ink)' }}>
            <CheckCircle2 size={13} color="var(--deep-enterprise-green)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <span>
              <strong>Semantic position:</strong>{' '}
              {topCandidate?.semantic_rank !== null && topCandidate?.semantic_rank !== undefined ? (
                <>
                  Ranked <strong>#{topCandidate.semantic_rank}</strong> in dense semantic retrieval
                  {topCandidate.semantic_score !== null && topCandidate.semantic_score !== undefined
                    ? ` (cosine similarity: ${topCandidate.semantic_score.toFixed(2)})`
                    : ''}
                  , contributing <code>1/(60 + {topCandidate.semantic_rank}) = {calcReciprocal(topCandidate.semantic_rank)}</code> to the RRF score.
                </>
              ) : (
                <>Did not appear in Top 30 dense semantic candidates (contributes 0.0 to RRF score).</>
              )}
            </span>
          </div>

          {/* Position in lexical */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px', color: 'var(--ink)' }}>
            <CheckCircle2 size={13} color="var(--deep-enterprise-green)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <span>
              <strong>Lexical position:</strong>{' '}
              {topCandidate?.lexical_rank !== null && topCandidate?.lexical_rank !== undefined ? (
                <>
                  Ranked <strong>#{topCandidate.lexical_rank}</strong> in sparse lexical keyword retrieval
                  {topCandidate.lexical_score !== null && topCandidate.lexical_score !== undefined
                    ? ` (TF-IDF overlap: ${topCandidate.lexical_score.toFixed(2)})`
                    : ''}
                  , contributing <code>1/(60 + {topCandidate.lexical_rank}) = {calcReciprocal(topCandidate.lexical_rank)}</code> to the RRF score.
                </>
              ) : (
                <>Did not appear in Top 30 lexical keyword candidates (contributes 0.0 to RRF score).</>
              )}
            </span>
          </div>

          {/* Combined RRF score */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px', color: 'var(--ink)' }}>
            <CheckCircle2 size={13} color="var(--deep-enterprise-green)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <span>
              <strong>Combined RRF score:</strong>{' '}
              <strong style={{ color: 'var(--deep-enterprise-green)' }}>
                {topCandidate?.rrf_score !== null && topCandidate?.rrf_score !== undefined
                  ? topCandidate.rrf_score.toFixed(5)
                  : (topCandidate?.final_score !== null && topCandidate?.final_score !== undefined ? topCandidate.final_score.toFixed(5) : '—')}
              </strong>
              . Reciprocal Rank Fusion ranks candidates that perform well across both semantic meaning and lexical vocabulary overlap highest.
            </span>
          </div>
        </div>
      </div>

      {/* 5. Required honesty / limitation footer: Never describe RRF as probability */}
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
        These scores are reciprocal rank fusion values (k = {k}) combining ordinal positions from semantic and lexical retrievers. They are ranking values, not calibrated probabilities.
      </div>
    </div>
  );
};
