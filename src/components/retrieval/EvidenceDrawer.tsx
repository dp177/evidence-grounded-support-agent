import React from 'react';
import { RetrievalEvidence } from '../../types/agent';
import { X, Copy, Check } from 'lucide-react';

interface EvidenceDrawerProps {
  evidence: RetrievalEvidence | null;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ evidence, onClose }) => {
  const [copied, setCopied] = React.useState(false);

  if (!evidence) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(evidence.case_id);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        padding: 'var(--space-16)',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '680px',
          backgroundColor: '#ffffff',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-light)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          maxHeight: '85vh',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: 'var(--space-16)',
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
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                color: '#ffffff',
                fontSize: '11px',
                fontFamily: 'var(--font-mono)',
                padding: '2px 8px',
                borderRadius: 'var(--radius-xs)',
              }}
            >
              HISTORICAL PRECEDENT
            </span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 600 }}>
              {evidence.case_id}
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
            <X size={18} />
          </button>
        </div>

        {/* Content Body */}
        <div
          style={{
            padding: 'var(--space-20)',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-16)',
            fontSize: '14px',
          }}
        >
          {/* Metadata banner */}
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
            <span>
              Conversation: <strong>{evidence.conversation_id}</strong>
            </span>
            <span>
              Turn: <strong>{evidence.turn_index}</strong>
            </span>
            <span>
              Vector Similarity: <strong>{evidence.similarity.toFixed(3)}</strong>
            </span>
            <button
              onClick={handleCopy}
              className="btn-secondary"
              style={{ padding: '2px 6px', fontSize: '11px', textDecoration: 'none' }}
            >
              {copied ? <Check size={12} color="var(--success-green)" /> : <Copy size={12} />}
              {copied ? 'Copied' : 'Copy ID'}
            </button>
          </div>

          {/* Customer Historical Query */}
          <div>
            <div className="mono-label" style={{ marginBottom: '4px' }}>
              Historical Customer Message
            </div>
            <div
              style={{
                padding: 'var(--space-12)',
                backgroundColor: '#f8f8f9',
                borderRadius: 'var(--radius-xs)',
                border: '1px solid var(--card-border)',
                lineHeight: '1.5',
              }}
            >
              {evidence.customer_message}
            </div>
          </div>

          {/* Context */}
          <div>
            <div className="mono-label" style={{ marginBottom: '4px' }}>
              Relevant Historical Context
            </div>
            <div
              style={{
                padding: 'var(--space-12)',
                backgroundColor: '#f8f8f9',
                borderRadius: 'var(--radius-xs)',
                border: '1px solid var(--card-border)',
                lineHeight: '1.5',
              }}
            >
              {evidence.relevant_context}
            </div>
          </div>

          {/* Amazon Brand Response */}
          <div>
            <div
              className="mono-label"
              style={{ marginBottom: '4px', color: 'var(--deep-enterprise-green)', fontWeight: 600 }}
            >
              Historical Amazon Brand Action & Response
            </div>
            <div
              style={{
                padding: 'var(--space-12)',
                backgroundColor: 'var(--pale-green-wash)',
                borderRadius: 'var(--radius-xs)',
                border: '1px solid rgba(0, 60, 51, 0.15)',
                color: 'var(--deep-enterprise-green)',
                lineHeight: '1.5',
                fontWeight: 500,
              }}
            >
              {evidence.brand_response}
            </div>
          </div>

          {/* Precedent vs Current Truth disclaimer */}
          <div
            style={{
              padding: 'var(--space-10)',
              borderRadius: 'var(--radius-xs)',
              backgroundColor: '#fffbeb',
              border: '1px solid #fef3c7',
              fontSize: '12px',
              color: '#92400e',
              lineHeight: '1.4',
            }}
          >
            <strong>Note on Historical Precedent:</strong> This retrieved case represents how Amazon previously resolved a past ticket. It does not reflect the current customer’s order records, credit balance, or account permissions.
          </div>
        </div>

        {/* Footer */}
        <div
          style={{
            padding: 'var(--space-12) var(--space-16)',
            backgroundColor: 'var(--soft-stone)',
            borderTop: '1px solid var(--border-light)',
            display: 'flex',
            justifyContent: 'flex-end',
          }}
        >
          <button onClick={onClose} className="btn-primary" style={{ fontSize: '13px', padding: '6px 16px' }}>
            Close Precedent
          </button>
        </div>
      </div>
    </div>
  );
};
