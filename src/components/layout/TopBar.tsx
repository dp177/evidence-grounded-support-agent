import React from 'react';
import { Cpu, ShieldCheck, Terminal } from 'lucide-react';
import { agentApi } from '../../services/agentApi';

interface TopBarProps {
  onToggleMockMode?: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({ onToggleMockMode }) => {
  const isMock = agentApi.isMock();

  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '56px',
        padding: '0 var(--space-24)',
        backgroundColor: 'var(--cohere-black)',
        color: '#ffffff',
        borderBottom: '1px solid #27272f',
      }}
    >
      {/* Left: Brand / App Name */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-12)' }}>
        <div
          style={{
            width: '28px',
            height: '28px',
            borderRadius: 'var(--radius-xs)',
            backgroundColor: 'var(--deep-enterprise-green)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
          }}
        >
          <Cpu size={16} />
        </div>
        <div>
          <span
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '15px',
              fontWeight: 600,
              letterSpacing: '-0.01em',
              color: '#ffffff',
            }}
          >
            AI Support Agent Console
          </span>
          <span
            style={{
              marginLeft: 'var(--space-8)',
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              color: 'var(--muted-slate)',
              textTransform: 'uppercase',
              letterSpacing: '0.4px',
            }}
          >
            AmazonHelp Enterprise
          </span>
        </div>
      </div>

      {/* Center: Environment & Model Badges */}
      <div
        className="topbar-center-badges"
        style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}
      >
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 'var(--space-4)',
            padding: '4px 10px',
            borderRadius: 'var(--radius-xl)',
            backgroundColor: '#1f1f26',
            color: '#d9d9dd',
            fontSize: '12px',
            fontFamily: 'var(--font-mono)',
            border: '1px solid #32323e',
          }}
        >
          <Terminal size={12} color="var(--muted-slate)" />
          ENV: LOCAL
        </span>

        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 'var(--space-4)',
            padding: '4px 10px',
            borderRadius: 'var(--radius-xl)',
            backgroundColor: '#1f1f26',
            color: '#d9d9dd',
            fontSize: '12px',
            fontFamily: 'var(--font-mono)',
            border: '1px solid #32323e',
          }}
        >
          MODEL: LLaMA 3.1 8B
        </span>

        {/* Mock vs Live Indicator */}
        <button
          onClick={onToggleMockMode}
          title="Toggle between deterministic Demo Data and Live Backend"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 'var(--space-6)',
            padding: '4px 10px',
            borderRadius: 'var(--radius-xl)',
            backgroundColor: isMock ? 'rgba(255, 119, 89, 0.15)' : 'rgba(13, 122, 85, 0.25)',
            color: isMock ? 'var(--coral)' : '#5eead4',
            border: `1px solid ${isMock ? 'var(--coral)' : '#14b8a6'}`,
            fontSize: '11px',
            fontFamily: 'var(--font-mono)',
            fontWeight: 600,
            cursor: 'pointer',
            letterSpacing: '0.3px',
          }}
        >
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: isMock ? 'var(--coral)' : '#14b8a6',
            }}
          />
          {isMock ? 'DEMO DATA' : 'LIVE AGENT'}
        </button>
      </div>

      {/* Right: Status & Safeguards */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-16)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: '#10b981',
              boxShadow: '0 0 0 2px rgba(16, 185, 129, 0.2)',
            }}
          />
          <span
            style={{
              fontSize: '12px',
              fontFamily: 'var(--font-mono)',
              color: '#d9d9dd',
              fontWeight: 500,
            }}
          >
            ONLINE
          </span>
        </div>

        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 'var(--space-6)',
            padding: '4px 10px',
            borderRadius: 'var(--radius-xl)',
            backgroundColor: 'rgba(0, 60, 51, 0.4)',
            color: '#a7f3d0',
            border: '1px solid rgba(167, 243, 208, 0.25)',
            fontSize: '11px',
            fontFamily: 'var(--font-mono)',
          }}
        >
          <ShieldCheck size={13} color="#a7f3d0" />
          HITL: ACTIVE
        </div>
      </div>
    </header>
  );
};
