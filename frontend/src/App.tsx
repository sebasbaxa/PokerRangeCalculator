import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';
import HandSelector from './components/HandSelector';
import SimulationSettings from './components/SimulationSettings';

interface HandResult {
  win_rate: number;
  hand: any;
}

interface Results {
  [key: string]: HandResult;
}

const App: React.FC = () => {
  const [results, setResults] = useState<Results>({});
  const [numSimulations, setNumSimulations] = useState(100);
  const [showHeroSelector, setShowHeroSelector] = useState(false);
  const [showVillainSelector, setShowVillainSelector] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [progress, setProgress] = useState({ completed: 0, total: 0 });
  const [error, setError] = useState<string>('');
  const eventSourceRef = useRef<EventSource | null>(null);

  const ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'];

  const getHandLabel = (row: number, col: number): string => {
    const rankValues = [14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2];
    const rowChar = ranks[row];
    const colChar = ranks[col];

    if (row === col) {
      // Pocket pairs on diagonal
      return `${rowChar}${rowChar}`;
    }

    const rowValue = rankValues[row];
    const colValue = rankValues[col];
    const highChar = rowValue >= colValue ? rowChar : colChar;
    const lowChar = rowValue >= colValue ? colChar : rowChar;

    if (row < col) {
      // Suited hands above diagonal
      return `${highChar}${lowChar}s`;
    }

    // Offsuit hands below diagonal
    return `${highChar}${lowChar}o`;
  };

  const getColor = (winRate: number): string => {
    if (winRate > 0.8) return '#4CAF50';
    if (winRate > 0.6) return '#FF9800';
    if (winRate > 0.45) return '#FFEB3B';
    return '#FFFFFF';
  };

  const startSimulation = async () => {
    setIsSimulating(true);
    setProgress({ completed: 0, total: 0 });
    setResults({});
    setError('');

    try {
      console.log('Starting simulation with', numSimulations, 'simulations');
      
      // Start simulation
      const response = await axios.post('/api/simulate', {
        num_simulations: numSimulations
      });

      console.log('Simulation started, task_id:', response.data.task_id);

      const taskId = response.data.task_id;

      // Connect to SSE stream for live updates
      const eventSource = new EventSource(`http://localhost:5000/api/simulate/stream/${taskId}`);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log('SSE connection opened');
      };

      eventSource.onmessage = (event) => {
        console.log('SSE message received:', event.data);
        
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'progress') {
            // Update single hand result
            console.log(`Progress: ${data.label} = ${data.win_rate}`);
            setResults(prev => ({
              ...prev,
              [data.label]: {
                win_rate: data.win_rate,
                hand: null
              }
            }));
            setProgress({ completed: data.completed, total: data.total });
          } else if (data.type === 'complete') {
            // Simulation finished
            console.log('Simulation complete!', data.results);
            setResults(data.results);
            setIsSimulating(false);
            eventSource.close();
            eventSourceRef.current = null;
          } else if (data.type === 'error') {
            console.error('Simulation error:', data.error);
            setError(data.error || 'Unknown error during simulation');
            setIsSimulating(false);
            eventSource.close();
            eventSourceRef.current = null;
          }
        } catch (e) {
          console.error('Error parsing SSE data:', e);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        setError('Connection to server lost. Please try again.');
        setIsSimulating(false);
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
      };

    } catch (error: any) {
      console.error('Simulation error:', error);
      const errorMsg = error.response?.data?.error || error.message || 'Failed to start simulation';
      setError(errorMsg);
      setIsSimulating(false);
    }
  };

  const stopSimulation = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsSimulating(false);
  };

  const resetRanges = async () => {
    try {
      await axios.delete('/api/ranges/hero');
      await axios.delete('/api/ranges/villain');
      setResults({});
      setProgress({ completed: 0, total: 0 });
      setError('');
    } catch (error) {
      console.error('Reset error:', error);
      setError('Failed to reset ranges');
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  return (
    <div className="app">
      <header className="header">
        <h1>Poker Range Calculator</h1>
        <nav className="nav">
          <button onClick={() => setShowHeroSelector(true)} className="btn btn-primary">
            Hero Range
          </button>
          <button onClick={() => setShowVillainSelector(true)} className="btn btn-primary">
            Villain Range
          </button>
          <button onClick={() => setShowSettings(true)} className="btn btn-secondary">
            Simulation Settings
          </button>
        </nav>
        {error && (
          <div className="error-banner">
            {error}
            <button onClick={() => setError('')} className="error-close">×</button>
          </div>
        )}
        {isSimulating && progress.total > 0 && (
          <div className="progress-bar">
            <div className="progress-text">
              Simulating: {progress.completed} / {progress.total}
            </div>
            <div className="progress-fill" style={{ width: `${(progress.completed / progress.total) * 100}%` }}></div>
          </div>
        )}
      </header>

      <main className="main">
        <div className="hand-grid">
          {ranks.map((_, rowIndex) => (
            <div key={rowIndex} className="grid-row">
              {ranks.map((_, colIndex) => {
                const label = getHandLabel(rowIndex, colIndex);
                const result = results[label];
                const winRate = result ? result.win_rate * 100 : 0;

                return (
                  <div
                    key={colIndex}
                    className="grid-cell"
                    style={{ backgroundColor: getColor(result?.win_rate || 0) }}
                  >
                    <div className="hand-label">{label}</div>
                    <div className="win-rate">{winRate.toFixed(2)}%</div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </main>

      <footer className="footer">
        {isSimulating ? (
          <button onClick={stopSimulation} className="btn btn-danger">
            Stop Simulation
          </button>
        ) : (
          <button onClick={startSimulation} className="btn btn-success">
            Run Calculation
          </button>
        )}
        <button onClick={resetRanges} className="btn btn-danger" disabled={isSimulating}>
          Reset Ranges
        </button>
      </footer>

      {showHeroSelector && (
        <HandSelector
          rangeType="hero"
          onClose={() => setShowHeroSelector(false)}
        />
      )}

      {showVillainSelector && (
        <HandSelector
          rangeType="villain"
          onClose={() => setShowVillainSelector(false)}
        />
      )}

      {showSettings && (
        <SimulationSettings
          open={showSettings}
          onClose={() => setShowSettings(false)}
          onApply={setNumSimulations}
        />
      )}
    </div>
  );
};

export default App;