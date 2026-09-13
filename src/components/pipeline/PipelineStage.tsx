import React from 'react';
import { StageInfo } from '../../types/agent';
import { Check, Loader2, AlertTriangle, XCircle, Circle } from 'lucide-react';

interface PipelineStageProps {
  stage: StageInfo;
  isActive: boolean;
  onClick: () => void;
}

export const PipelineStage: React.FC<PipelineStageProps> = ({
  stage,
  isActive,
  onClick,
}) => {
  const getStatusIcon = () => {
    switch (stage.status) {
      case 'SUCCESS':
        return <Check size={12} color="#ffffff" />;
      case 'RUNNING':
        return <Loader2 size={12} className="spin-animation" color="#ffffff" />;
      case 'WARNING':
        return <AlertTriangle size={12} color="#ffffff" />;
      case 'FAILED':
        return <XCircle size={12} color="#ffffff" />;
      default:
        return <Circle size={8} color="var(--muted-slate)" />;
    }
  };

  const getBadgeBg = () => {
    switch (stage.status) {
      case 'SUCCESS':
        return 'var(--deep-enterprise-green)';
      case 'RUNNING':
        return 'var(--action-blue)';
      case 'WARNING':
        return '#d97706';
      case 'FAILED':
        return 'var(--error-red)';
      default:
        return 'transparent';
    }
  };

  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-6)',
        padding: '5px 12px',
        borderRadius: 'var(--radius-xl)',
        backgroundColor: isActive ? 'var(--soft-stone)' : 'transparent',
        border: isActive ? '1px solid var(--slate)' : '1px solid transparent',
        cursor: 'pointer',
        fontFamily: 'var(--font-mono)',
        fontSize: '12px',
        color: stage.status === 'IDLE' ? 'var(--muted-slate)' : 'var(--ink)',
        fontWeight: isActive ? 600 : 500,
        transition: 'all 0.15s ease',
      }}
    >
      <span
        style={{
          width: '18px',
          height: '18px',
          borderRadius: '50%',
          backgroundColor: getBadgeBg(),
          border: stage.status === 'IDLE' ? '1px solid var(--hairline)' : 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {getStatusIcon()}
      </span>
      <span>{stage.name}</span>
    </button>
  );
};
