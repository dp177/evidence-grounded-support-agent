import React from 'react';
import { ArrowRight, Filter, Users } from 'lucide-react';

interface CandidateListProps {
  candidateCount: number;
  finalCount: number;
  uniqueConversations: number;
}

export const CandidateList: React.FC<CandidateListProps> = ({
  candidateCount,
  finalCount,
  uniqueConversations,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 'var(--space-10) var(--space-12)',
        backgroundColor: 'var(--soft-stone)',
        borderRadius: 'var(--radius-xs)',
        fontSize: '12px',
        fontFamily: 'var(--font-mono)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
        <Filter size={13} color="var(--slate)" />
        <span>
          <strong>{candidateCount}</strong> candidates
        </span>
        <ArrowRight size={12} color="var(--muted-slate)" />
        <span style={{ color: 'var(--deep-enterprise-green)', fontWeight: 600 }}>
          <strong>{finalCount}</strong> final precedent cases
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', color: 'var(--slate)' }}>
        <Users size={12} />
        <span>{uniqueConversations} unique threads</span>
      </div>
    </div>
  );
};
