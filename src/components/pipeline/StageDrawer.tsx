import React from 'react';
import { StageName, AgentResponse } from '../../types/agent';
import { X } from 'lucide-react';

interface StageDrawerProps {
  stageName: StageName | null;
  response: AgentResponse | null;
  onClose: () => void;
}

export const StageDrawer: React.FC<StageDrawerProps> = ({
  stageName,
  response,
  onClose,
}) => {
  if (!stageName) return null;

  const renderStageContent = () => {
    if (!response) {
      return (
        <div style={{ padding: 'var(--space-20)', color: 'var(--muted-slate)', fontSize: '13px' }}>
          Stage diagnostics will populate when the agent pipeline executes.
        </div>
      );
    }

    switch (stageName) {
      case 'Conversation':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-12)' }}>
            <div>
              <span className="mono-label">Session ID</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', marginTop: '2px' }}>
                {response.conversation_id}
              </div>
            </div>
            <div>
              <span className="mono-label">Turn Focus</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', marginTop: '2px' }}>
                Customer input query: "{response.retrieval_query.customer_query}"
              </div>
            </div>
          </div>
        );

      case 'Classify':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-12)' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <span className="mono-label">Classifier Engine</span>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                  Classifier V2 (Few-Shot Prompted)
                </div>
              </div>
              <div>
                <span className="mono-label">Taxonomy Version</span>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                  {response.classification.taxonomy_version || 'Taxonomy V1 (10 L1 Domains)'}
                </div>
              </div>
            </div>
            <div>
              <span className="mono-label">Primary Intent</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 600, marginTop: '2px' }}>
                {response.classification.primary_intent}
              </div>
            </div>
            <div>
              <span className="mono-label">Conversation States</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                {response.classification.states.join(', ')}
              </div>
            </div>
            <div>
              <span className="mono-label">Softmax Confidence</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                {(response.classification.confidence * 100).toFixed(1)}% (Uncalibrated estimate)
              </div>
            </div>
          </div>
        );

      case 'Retrieve':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-12)' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <span className="mono-label">Vector Store</span>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                  Qdrant Vector DB (Cosine)
                </div>
              </div>
              <div>
                <span className="mono-label">Embedding Model</span>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                  BAAI/bge-small-en-v1.5 (384-dim)
                </div>
              </div>
            </div>
            <div>
              <span className="mono-label">Semantic Query</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                "{response.retrieval_query.customer_query}"
              </div>
            </div>
            <div>
              <span className="mono-label">Candidates Retrieved</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                Top 30 initial vector neighbors
              </div>
            </div>
          </div>
        );

      case 'Rerank':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-12)' }}>
            <div>
              <span className="mono-label">Funnel Configuration</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                30 semantic + 30 lexical candidates → {response.retrieved_evidence.length} precedent evidence cases
              </div>
            </div>
            <div>
              <span className="mono-label">Fusion Method</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                Reciprocal Rank Fusion (k = {response.reranking.k || 60})
              </div>
            </div>
            <div>
              <span className="mono-label">Conversation Diversity</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                {response.reranking.unique_conversations} distinct customer threads preserved
              </div>
            </div>
            <div>
              <span className="mono-label">Fusion Signals</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', marginTop: '4px', lineHeight: '1.5' }}>
                • Dense semantic cosine ranking (Top 30)<br />
                • Sparse TF-IDF lexical ranking (Top 30)<br />
                • RRF(d) = 1/(60 + sem_rank) + 1/(60 + lex_rank)
              </div>
            </div>
          </div>
        );


      case 'Generate':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-12)' }}>
            <div>
              <span className="mono-label">Generation Model</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                meta-llama/llama-3.1-8b-instruct
              </div>
            </div>
            <div>
              <span className="mono-label">Precedent Grounding Sources</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                {response.generated_reply.evidence_ids.join(', ') || 'None'}
              </div>
            </div>
            <div>
              <span className="mono-label">Revision Iteration</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', marginTop: '2px' }}>
                {response.generated_reply.revision_count === 0
                  ? 'Accepted on initial pass'
                  : `Revised ${response.generated_reply.revision_count} time(s) to remove unverified claims`}
              </div>
            </div>
          </div>
        );

      case 'Ground':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-12)' }}>
            <div>
              <span className="mono-label">Verification Score</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 600, marginTop: '2px' }}>
                {response.grounding.score.toFixed(2)} / 1.00
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
              <div>
                <span className="mono-label">Supported</span>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--success-green)' }}>
                  {response.grounding.supported_claims}
                </div>
              </div>
              <div>
                <span className="mono-label">Unsupported</span>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--coral)' }}>
                  {response.grounding.unsupported_claims}
                </div>
              </div>
              <div>
                <span className="mono-label">Contradicted</span>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--error-red)' }}>
                  {response.grounding.contradicted_claims}
                </div>
              </div>
            </div>
          </div>
        );

      case 'Decide':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-12)' }}>
            <div>
              <span className="mono-label">Policy Decision</span>
              <div
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '14px',
                  fontWeight: 700,
                  color:
                    response.escalation.decision === 'AUTO_HANDLE'
                      ? 'var(--success-green)'
                      : 'var(--error-red)',
                  marginTop: '2px',
                }}
              >
                {response.escalation.decision} ({response.escalation.action})
              </div>
            </div>
            <div>
              <span className="mono-label">Passed Policy Gates</span>
              <ul
                style={{
                  margin: '4px 0 0 16px',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  color: 'var(--success-green)',
                }}
              >
                {response.escalation.passed_gates.map((g) => (
                  <li key={g}>{g}</li>
                ))}
              </ul>
            </div>
            {response.escalation.blocker_reasons.length > 0 && (
              <div>
                <span className="mono-label" style={{ color: 'var(--error-red)' }}>
                  Escalation Trigger Blocker Rules
                </span>
                <ul
                  style={{
                    margin: '4px 0 0 16px',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    color: 'var(--error-red)',
                  }}
                >
                  {response.escalation.blocker_reasons.map((b) => (
                    <li key={b}>{b}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.4)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9998,
        padding: 'var(--space-16)',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '540px',
          backgroundColor: '#ffffff',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-light)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div
          style={{
            padding: 'var(--space-12) var(--space-16)',
            backgroundColor: 'var(--near-black-primary)',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
            <span
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '14px',
                fontWeight: 600,
              }}
            >
              Stage Diagnostics: {stageName}
            </span>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#ffffff',
              cursor: 'pointer',
            }}
          >
            <X size={16} />
          </button>
        </div>

        <div style={{ padding: 'var(--space-20)' }}>{renderStageContent()}</div>

        <div
          style={{
            padding: 'var(--space-12) var(--space-16)',
            backgroundColor: 'var(--soft-stone)',
            borderTop: '1px solid var(--border-light)',
            display: 'flex',
            justifyContent: 'flex-end',
          }}
        >
          <button onClick={onClose} className="btn-primary" style={{ fontSize: '12px', padding: '5px 14px' }}>
            Dismiss
          </button>
        </div>
      </div>
    </div>
  );
};
