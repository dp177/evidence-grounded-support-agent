import React from 'react';
import { Bookmark } from 'lucide-react';

interface EvidenceReferenceProps {
  evidenceIds: string[];
  onSelectEvidence?: (docId: string) => void;
}

export const EvidenceReference: React.FC<EvidenceReferenceProps> = ({
  evidenceIds,
  onSelectEvidence,
}) => {
  if (evidenceIds.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <span className="mono-label" style={{ fontSize: '10px' }}>
        HISTORICAL EVIDENCE PRECEDENTS CITED
      </span>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-6)' }}>
        {evidenceIds.map((id) => (
          <button
            key={id}
            type="button"
            onClick={() => onSelectEvidence && onSelectEvidence(id)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '3px 8px',
              borderRadius: 'var(--radius-xs)',
              backgroundColor: 'var(--soft-stone)',
              border: '1px solid var(--hairline)',
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              color: 'var(--ink)',
              cursor: onSelectEvidence ? 'pointer' : 'default',
              transition: 'all 0.15s ease',
            }}
          >
            <Bookmark size={11} color="var(--deep-enterprise-green)" />
            <span>[{id}]</span>
          </button>
        ))}
      </div>
    </div>
  );
};
