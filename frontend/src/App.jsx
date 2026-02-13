import { useState } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import ErrorBoundary from './components/ErrorBoundary';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Alerts from './pages/Alerts';
import Dashboard from './pages/Dashboard';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

function App() {
  const [lastUpdated, setLastUpdated] = useState('');

  const onSyncTick = () => {
    setLastUpdated(new Date().toLocaleTimeString());
  };

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <div className="min-h-screen">
          <div className="flex">
            <Sidebar />
            <div className="flex min-h-screen flex-1 flex-col">
              <Navbar lastUpdated={lastUpdated} />
              <main className="flex-1 p-4 sm:p-6">
                <Routes>
                  <Route path="/" element={<Dashboard onSyncTick={onSyncTick} />} />
                  <Route path="/alerts" element={<Alerts onSyncTick={onSyncTick} />} />
                  <Route path="/reports" element={<Reports />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </main>
            </div>
          </div>
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
