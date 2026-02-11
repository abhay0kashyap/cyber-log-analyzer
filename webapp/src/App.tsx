/**
 * Cyber Log Analyzer - Main App Component
 * SIEM Dashboard Application
 */

import React from 'react';
import Dashboard from './pages/Dashboard';
import MainLayout from './layout/MainLayout';

function App() {
  return (
    <MainLayout>
      <Dashboard />
    </MainLayout>
  );
}

export default App;

