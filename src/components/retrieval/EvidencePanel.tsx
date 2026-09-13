import React, { useState } from 'react';
import { RetrievalEvidence } from '../../types/agent';
import { EvidenceCard } from './EvidenceCard';
import { EvidenceDrawer } from './EvidenceDrawer';
import { Database, Search, ChevronDown, ChevronUp } from 'lucide-react';

interface EvidencePanelProps {
  evidenceList: RetrievalEvidence[];
  retrievalQuery?: {
    customer_query: string;
    context: string;
  };
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  evidenceList,
  retrievalQuery,
}) => {
  const [selectedEvidence, setSelectedEvidence] = useState<RetrievalEvidence | null>(null);
  const [showQuery, setShowQuery] = useState(false);

  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-sm)',
        padding: 'var(--space-16)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-12)',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--card-border)',
          paddingBottom: 'var(--space-10)',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
            <Database size={15} color="var(--deep-enterprise-green)" />
            <h3
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: '14px',
                fontWeight: 600,
                color: 'var(--cohere-black)',
              }}
            >
              Historical Evidence
            </h3>
          </div>
          <p
            style={{
              fontSize: '12px',
              color: 'var(--slate)',
              marginTop: 'var(--space-2)',
            }}
          >
            Real Amazon support interactions used as precedent.
          </p>
        </div>

        <span className="mono-label" style={{ fontSize: '11px' }}>
          {evidenceList.length} CASES
        </span>
      </div>

      {/* Expandable Retrieval Query Display (Section 14) */}
      {retrievalQuery && (
        <div
          style={{
            borderRadius: 'var(--radius-xs)',
            backgroundColor: '#fafafb',
            border: '1px solid var(--border-light)',
            overflow: 'hidden',
          }}
        >
          <button
            onClick={() => setShowQuery(!showQuery)}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: 'var(--space-8) var(--space-10)',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              color: 'var(--slate)',
              fontWeight: 600,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
              <Search size={12} />
              <span>RETRIEVAL QUERY SENT TO QDRANT</span>
            </div>
            {showQuery ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>

          {showQuery && (
            <div
              style={{
                padding: 'var(--space-10)',
                borderTop: '1px solid var(--hairline)',
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--space-6)',
                fontSize: '12px',
              }}
            >
              <div>
                <span className="mono-label" style={{ fontSize: '10px' }}>
                  Customer Query Vector Seed:
                </span>
                <div style={{ color: 'var(--ink)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
                  "{retrievalQuery.customer_query}"
                </div>
              </div>
              {retrievalQuery.context && (
                <div>
                  <span className="mono-label" style={{ fontSize: '10px' }}>
                    Conversation Context Payload:
                  </span>
                  <div style={{ color: 'var(--slate)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
                    {retrievalQuery.context}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* List of Evidence Cards (Top 5) */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-10)' }}>
        {evidenceList.length === 0 ? (
          <div
            style={{
              padding: 'var(--space-16)',
              textAlign: 'center',
              color: 'var(--muted-slate)',
              fontSize: '13px',
              border: '1px dashed var(--hairline)',
              borderRadius: 'var(--radius-xs)',
            }}
          >
            No historical precedent cases retrieved yet.
          </div>
        ) : (
          evidenceList.slice(0, 5).map((ev, idx) => (
            <EvidenceCard
              key={ev.case_id}
              evidence={ev}
              onOpenDetails={(item) => setSelectedEvidence(item)}
              initiallyExpanded={idx === 0}
            />
          ))
        )}
      </div>

      {/* Precedent detail drawer */}
      <EvidenceDrawer
        evidence={selectedEvidence}
        onClose={() => setSelectedEvidence(null)}
      />
    </div>
  );
};
