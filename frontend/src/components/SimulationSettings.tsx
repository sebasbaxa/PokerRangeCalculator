import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SimulationSettings.css';

interface SimulationSettingsProps {
  open: boolean;
  onClose: () => void;
  onApply: (num: number) => void;
}

const SimulationSettings: React.FC<SimulationSettingsProps> = ({ open, onClose, onApply }) => {
  const [value, setValue] = useState(100);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!open) return;
    (async () => {
      try {
        const res = await axios.get('/api/settings');
        setValue(res.data.num_simulations);
      } catch {
        // ignore
      }
    })();
  }, [open]);

  const handleApply = async () => {
    setError('');
    const num = Number(value);
    
    if (!Number.isInteger(num) || num <= 0) {
      setError('Enter a positive integer.');
      return;
    }

    setLoading(true);
    try {
      await axios.post('/api/settings', { num_simulations: num });
      onApply(num);
      onClose();
    } catch {
      setError('Failed to save.');
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
        <h2>Simulation Settings</h2>
        <label>
          Number of simulations per hand:
          <input
            type="number"
            value={value}
            onChange={(e) => setValue(Number(e.target.value))}
            min={1}
          />
        </label>
        {error && <div className="error">{error}</div>}
        <div className="buttons">
          <button onClick={handleApply} disabled={loading} className="btn btn-primary">
            {loading ? 'Saving...' : 'Apply'}
          </button>
          <button onClick={onClose} disabled={loading} className="btn btn-secondary">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default SimulationSettings;