import React, { useState } from 'react';
import { MessageSquare, Search, ShieldCheck } from 'lucide-react';

interface AppShellProps {
  topBar: React.ReactNode;
  pipelineStepper: React.ReactNode;
  statusBar: React.ReactNode;
  demoSelector: React.ReactNode;
  tracePanel: React.ReactNode;
  conversationCol: React.ReactNode;
  intelligenceCol: React.ReactNode;
  responseCol: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({
  topBar,
  pipelineStepper,
  statusBar,
  demoSelector,
  tracePanel,
  conversationCol,
  intelligenceCol,
  responseCol,
}) => {
  const [mobileTab, setMobileTab] = useState<'conversation' | 'intelligence' | 'response'>('conversation');

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        backgroundColor: 'var(--canvas-white)',
      }}
    >
      {/* 1. Global Top Navigation */}
      {topBar}

      {/* 2. Demo Scenario Control Bar */}
      {demoSelector}

      {/* 3. Pipeline Stepper Status */}
      {pipelineStepper}

      {/* 4. Session Status Bar */}
      {statusBar}

      {/* Mobile Tab Switcher (Visible only on small viewports via CSS) */}
      <div className="mobile-tab-bar" style={{ display: 'none' }}>
        <button
          className={mobileTab === 'conversation' ? 'active' : ''}
          onClick={() => setMobileTab('conversation')}
        >
          <MessageSquare size={14} /> Conversation
        </button>
        <button
          className={mobileTab === 'intelligence' ? 'active' : ''}
          onClick={() => setMobileTab('intelligence')}
        >
          <Search size={14} /> AI Analysis
        </button>
        <button
          className={mobileTab === 'response' ? 'active' : ''}
          onClick={() => setMobileTab('response')}
        >
          <ShieldCheck size={14} /> Response & Safety
        </button>
      </div>

      {/* 5. Main 3-Column Workspace */}
      <main
        className="app-main-workspace"
        style={{
          flex: 1,
          display: 'grid',
          gridTemplateColumns: 'minmax(360px, 420px) minmax(400px, 1fr) minmax(400px, 1fr)',
          gap: 'var(--space-20)',
          maxWidth: '1680px',
          width: '100%',
          margin: '0 auto',
          padding: 'var(--space-20) var(--space-24)',
        }}
      >
        {/* Left Column: Live Customer Conversation */}
        <section
          className={`workspace-col col-conversation ${mobileTab === 'conversation' ? 'mobile-show' : 'mobile-hide'}`}
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-16)',
            minWidth: 0,
          }}
        >
          {conversationCol}
        </section>

        {/* Center Column: AI Investigation & Historical Precedent */}
        <section
          className={`workspace-col col-intelligence ${mobileTab === 'intelligence' ? 'mobile-show' : 'mobile-hide'}`}
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-16)',
            minWidth: 0,
          }}
        >
          {intelligenceCol}
        </section>

        {/* Right Column: Generation, Grounding & Escalation Action */}
        <section
          className={`workspace-col col-response ${mobileTab === 'response' ? 'mobile-show' : 'mobile-hide'}`}
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-16)',
            minWidth: 0,
          }}
        >
          {responseCol}
        </section>
      </main>

      {/* 6. Observability & Latency Breakdown Panel (Footer Drawer) */}
      {tracePanel}

      {/* Responsive Media Styles */}
      <style>{`
        @media (max-width: 1180px) {
          .app-main-workspace {
            grid-template-columns: 1fr 1fr !important;
          }
          .col-conversation {
            grid-column: 1 / -1;
          }
        }

        @media (max-width: 768px) {
          .topbar-center-badges {
            display: none !important;
          }
          .mobile-tab-bar {
            display: flex !important;
            border-bottom: 1px solid var(--border-light);
            background-color: var(--soft-stone);
          }
          .mobile-tab-bar button {
            flex: 1;
            padding: 10px;
            background: none;
            border: none;
            font-family: var(--font-body);
            font-size: 13px;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            cursor: pointer;
            color: var(--slate);
            border-bottom: 2px solid transparent;
          }
          .mobile-tab-bar button.active {
            color: var(--ink);
            border-bottom-color: var(--near-black-primary);
            background-color: #ffffff;
          }
          .app-main-workspace {
            display: flex !important;
            flex-direction: column;
            padding: var(--space-12) !important;
          }
          .mobile-hide {
            display: none !important;
          }
          .mobile-show {
            display: flex !important;
          }
        }
      `}</style>
    </div>
  );
};
