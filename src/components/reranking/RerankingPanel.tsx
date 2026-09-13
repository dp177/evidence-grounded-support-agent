import React from 'react';
import { RerankingResult } from '../../types/agent';
import { RankingSignal } from './RankingSignal';
import { CandidateList } from './CandidateList';
import { Sparkles } from 'lucide-react';

interface RerankingPanelProps {
  reranking?: RerankingResult | null;
}

export const RerankingPanel: React.FC<RerankingPanelProps> = ({ reranking }) => {
  if (!reranking) {
    return null;
  }

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

      {/* Candidate Funnel */}
      <CandidateList
        candidateCount={reranking.candidate_count}
        finalCount={reranking.final_count}
        uniqueConversations={reranking.unique_conversations}
      />

      {/* Signals Breakdown */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
        <span className="mono-label" style={{ fontSize: '10px' }}>
          RANKING COMPATIBILITY SIGNALS
        </span>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
          {reranking.signals.map((sig) => (
            <RankingSignal key={sig.name} signal={sig} />
          ))}
        </div>
      </div>
    </div>
  );
};
