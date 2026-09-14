import React from 'react';

export const TopBar: React.FC = () => {
  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '60px',
        padding: '0 var(--space-24)',
        backgroundColor: '#ffffff',
        color: '#0f1111', // Amazon default text color
        borderBottom: '1px solid #d5d9d9',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      }}
    >
      {/* Left: Brand / App Name */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
        <div
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '22px',
            fontWeight: 700,
            letterSpacing: '-0.02em',
            color: '#0f1111',
          }}
        >
          amazon<span style={{ color: '#ff9900' }}>help</span>
        </div>
      </div>

    </header>
  );
};
