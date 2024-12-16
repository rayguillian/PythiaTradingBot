import React from 'react';
import './styles/global.css';
import PythiaDashboard from './components/PythiaDashboard';
import StrategyConfiguration from './components/StrategyConfiguration';

const App: React.FC = () => {
  return (
    <div className="app">
      <nav className="app-nav">
        <h1>Pythia Trading Bot</h1>
      </nav>
      <main className="app-main">
        <PythiaDashboard />
        <StrategyConfiguration />
      </main>
    </div>
  );
};

export default App;
