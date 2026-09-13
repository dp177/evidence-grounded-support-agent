import React, { useState } from 'react';
import { RetrievalEvidence, RerankingResult } from '../../types/agent';
import { Database, ChevronDown, ChevronUp, Layers } from 'lucide-react';

interface InlineEvidenceProps {
  evidenceList: RetrievalEvidence[];
  reranking?: RerankingResult;
}

export const InlineEvidence: React.FC<InlineEvidenceProps> = ({
  evidenceList,
  reranking,
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
            padding: '10px 14px',
            backgroundColor: '#f1f5f9',
            borderBottom: '1px solid var(--border-light)',
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
          }}
        >
          {reranking ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--ink)' }}>
                <strong>Multi-Stage Reranker Funnel:</strong>
                <span>
                  {reranking.candidate_count} candidates → {reranking.final_count} selected ({reranking.unique_conversations} threads)
                </span>
              </div>

              {reranking.signals && reranking.signals.length > 0 ? (
                <div>
                  <span style={{ fontSize: '10px', color: 'var(--slate)' }}>Compatibility Signals:</span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '3px' }}>
                    {reranking.signals.map((sig) => (
                      <span
                        key={sig.name}
                        style={{
                          padding: '2px 6px',
                          borderRadius: '2px',
                          backgroundColor: '#ffffff',
                          border: '1px solid #cbd5e1',
                          fontSize: '10px',
                        }}
                      >
                        {sig.label}: <strong>{sig.score}%</strong>
                      </span>
                    ))}
                  </div>
                </div>
              ) : (
                <div style={{ color: 'var(--slate)', fontStyle: 'italic', fontSize: '10px' }}>
                  Detailed ranking information unavailable
                </div>
              )}
            </div>
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
