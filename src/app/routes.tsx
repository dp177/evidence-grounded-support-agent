import React, { useEffect, useState } from 'react';
import { App } from './App';

export const Router: React.FC = () => {
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  useEffect(() => {
    // If root '/', redirect or render /support
    if (window.location.pathname === '/' || window.location.pathname === '') {
      window.history.replaceState(null, '', '/support');
      setCurrentPath('/support');
    }

    const handlePop = () => {
      setCurrentPath(window.location.pathname);
    };

    window.addEventListener('popstate', handlePop);
    return () => window.removeEventListener('popstate', handlePop);
  }, []);

  // Main support console route
  if (currentPath === '/support' || currentPath === '/' || currentPath.startsWith('/support')) {
    return <App />;
  }

  return <App />;
};
