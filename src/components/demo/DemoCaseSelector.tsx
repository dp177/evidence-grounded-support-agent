import React from 'react';
import { DemoScenario } from '../../types/agent';
import { Layers } from 'lucide-react';

interface DemoCaseSelectorProps {
  scenarios: DemoScenario[];
  selectedScenarioId: string;
  onSelectScenario: (scenario: DemoScenario) => void;
  isRunning: boolean;
}

export const DemoCaseSelector: React.FC<DemoCaseSelectorProps> = ({
  scenarios,
  selectedScenarioId,
  onSelectScenario,
  isRunning,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-12)',
        padding: 'var(--space-8) var(--space-24)',
        backgroundColor: 'var(--soft-stone)',
        borderBottom: '1px solid var(--border-light)',
        overflowX: 'auto',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-6)',
          flexShrink: 0,
          color: 'var(--ink)',
        }}
      >
        <Layers size={14} color="var(--deep-enterprise-green)" />
        <span
          className="mono-label"
          style={{ fontSize: '11px', fontWeight: 600, color: 'var(--ink)' }}
        >
          DEMO SCENARIOS:
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
        {scenarios.map((sc) => {
          const isSelected = sc.id === selectedScenarioId;
          const isSecurity = sc.id === 'demo-account-hacked';
          const isAmbiguous = sc.id === 'demo-ambiguous-complaint';

          return (
            <button
              key={sc.id}
              type="button"
              disabled={isRunning}
              onClick={() => onSelectScenario(sc)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 'var(--space-6)',
                padding: '4px 12px',
                borderRadius: 'var(--radius-xl)',
                backgroundColor: isSelected ? 'var(--near-black-primary)' : '#ffffff',
                color: isSelected
                  ? '#ffffff'
                  : isSecurity
                  ? 'var(--error-red)'
                  : isAmbiguous
                  ? '#c2410c'
                  : 'var(--ink)',
                border: isSelected
                  ? '1px solid var(--near-black-primary)'
                  : isSecurity
                  ? '1px solid rgba(179, 0, 0, 0.3)'
                  : '1px solid var(--border-light)',
                fontFamily: 'var(--font-body)',
                fontSize: '12px',
                fontWeight: isSelected ? 600 : 500,
                cursor: isRunning ? 'not-allowed' : 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.15s ease',
              }}
            >
              <span>{sc.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
