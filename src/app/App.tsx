import React from 'react';
import { TopBar } from '../components/layout/TopBar';
import { CustomLiveChat } from '../components/custom/CustomLiveChat';

export const App: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: 'var(--canvas-white)' }}>
      {/* 1. Global Navigation */}
      <TopBar />

      {/* 2. Chat Interface */}
      <CustomLiveChat />
    </div>
  );
};

export default App;
