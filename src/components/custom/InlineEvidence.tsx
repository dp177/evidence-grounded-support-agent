import React, { useState } from 'react';
import { RetrievalEvidence } from '../../types/agent';
import { Database, ChevronDown, ChevronUp } from 'lucide-react';

interface InlineEvidenceProps {
  evidenceList: RetrievalEvidence[];
}

export const InlineEvidence: React.FC<InlineEvidenceProps> = ({ evidenceList }) => {
  const [expanded, setExpanded] = useState(false);

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
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '6px 12px',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Database size={12} color="var(--deep-enterprise-green)" />
          <span style={{ color: 'var(--slate)' }}>Historical Precedent ·</span>
          <strong style={{ color: 'var(--ink)' }}>
            {evidenceList.length} precedents cited
          </strong>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--slate)' }}>
          <span>{expanded ? 'Hide' : 'Inspect precedents'}</span>
          {expanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
        </div>
      </button>

      {expanded && (
        <div
          style={{
            padding: '10px 14px',
            borderTop: '1px solid var(--border-light)',
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
                padding: '8px 10px',
                borderRadius: 'var(--radius-xs)',
                backgroundColor: '#ffffff',
                border: '1px solid var(--card-border)',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px',
                fontSize: '11px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
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
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--action-blue)', fontWeight: 600 }}>
                  SIM: {ev.similarity.toFixed(2)}
                </span>
              </div>

              <div style={{ color: 'var(--slate)', fontSize: '11px', lineHeight: '1.4' }}>
                <strong>Customer:</strong> "{ev.customer_message}"
              </div>

              <div
                style={{
                  color: 'var(--deep-enterprise-green)',
                  fontSize: '11px',
                  lineHeight: '1.4',
                  backgroundColor: 'var(--pale-green-wash)',
                  padding: '4px 6px',
                  borderRadius: '2px',
                }}
              >
                <strong>Amazon Action:</strong> {ev.brand_response}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
