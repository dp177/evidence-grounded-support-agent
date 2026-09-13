import React, { useState } from 'react';
import { RetrievalEvidence } from '../../types/agent';
import { EvidenceScore } from './EvidenceScore';
import { ChevronDown, ChevronUp, Copy, Check, Eye } from 'lucide-react';

interface EvidenceCardProps {
  evidence: RetrievalEvidence;
  onOpenDetails: (evidence: RetrievalEvidence) => void;
  initiallyExpanded?: boolean;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({
  evidence,
  onOpenDetails,
  initiallyExpanded = false,
}) => {
  const [expanded, setExpanded] = useState(initiallyExpanded);
  const [copied, setCopied] = useState(false);

  const copyCaseId = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(evidence.case_id);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-sm)',
        overflow: 'hidden',
        transition: 'border-color 0.15s ease',
      }}
    >
      {/* Summary Header (Always Visible) */}
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: 'var(--space-10) var(--space-12)',
          backgroundColor: '#fafafb',
          cursor: 'pointer',
          borderBottom: expanded ? '1px solid var(--border-light)' : 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
          {/* MANDATORY BADGE */}
          <span
            style={{
              padding: '2px 8px',
              borderRadius: 'var(--radius-xs)',
              backgroundColor: 'var(--near-black-primary)',
              color: '#ffffff',
              fontSize: '10px',
              fontFamily: 'var(--font-mono)',
              fontWeight: 600,
              letterSpacing: '0.4px',
            }}
          >
            HISTORICAL PRECEDENT
          </span>

          <span
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              fontWeight: 600,
              color: 'var(--ink)',
            }}
          >
            {evidence.case_id}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
          <EvidenceScore score={evidence.similarity} />

          <button
            onClick={copyCaseId}
            title="Copy Case ID"
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--slate)',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            {copied ? <Check size={13} color="var(--success-green)" /> : <Copy size={13} />}
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onOpenDetails(evidence);
            }}
            title="Open Precedent Full View"
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--slate)',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <Eye size={13} />
          </button>

          <span style={{ color: 'var(--slate)' }}>
            {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </span>
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div
          style={{
            padding: 'var(--space-12) var(--space-14)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-10)',
            fontSize: '13px',
          }}
        >
          {/* Historical Customer Query */}
          <div>
            <div className="mono-label" style={{ fontSize: '10px' }}>
              Customer Message
            </div>
            <div
              style={{
                marginTop: 'var(--space-2)',
                color: 'var(--ink)',
                lineHeight: '1.4',
                fontSize: '13px',
              }}
            >
              "{evidence.customer_message}"
            </div>
          </div>

          {/* Relevant Context */}
          <div>
            <div className="mono-label" style={{ fontSize: '10px' }}>
              Historical Context
            </div>
            <div
              style={{
                marginTop: 'var(--space-2)',
                color: 'var(--slate)',
                fontSize: '12px',
                lineHeight: '1.4',
              }}
            >
              {evidence.relevant_context}
            </div>
          </div>

          {/* Amazon Brand Response */}
          <div
            style={{
              marginTop: 'var(--space-4)',
              padding: 'var(--space-8) var(--space-10)',
              backgroundColor: 'var(--soft-stone)',
              borderRadius: 'var(--radius-xs)',
              borderLeft: '3px solid var(--deep-enterprise-green)',
            }}
          >
            <div
              className="mono-label"
              style={{
                fontSize: '10px',
                color: 'var(--deep-enterprise-green)',
                fontWeight: 600,
              }}
            >
              Historical Amazon Precedent Action
            </div>
            <div
              style={{
                marginTop: 'var(--space-2)',
                color: 'var(--ink)',
                fontSize: '12px',
                lineHeight: '1.4',
              }}
            >
              {evidence.brand_response}
            </div>
          </div>

          {/* Case metadata footer */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              color: 'var(--muted-slate)',
              paddingTop: 'var(--space-4)',
            }}
          >
            <span>{evidence.conversation_id}</span>
            <button
              onClick={() => onOpenDetails(evidence)}
              className="btn-secondary"
              style={{ padding: '0', fontSize: '11px' }}
            >
              View Full Precedent →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
