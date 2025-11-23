import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './HandSelector.css';

interface HandSelectorProps {
  rangeType: 'hero' | 'villain';
  onClose: () => void;
}

const HandSelector: React.FC<HandSelectorProps> = ({ rangeType, onClose }) => {
  const ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'];
  const rankValues = [14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2];
  const [selectedHands, setSelectedHands] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadExistingRange();
  }, [rangeType]);

  const loadExistingRange = async () => {
    try {
      const response = await axios.get(`/api/ranges/${rangeType}`);
      const hands = response.data.hands;
      
      console.log(`Loading ${hands.length} hands for ${rangeType}`);
      
      // Count each unique hand combination
      const handCounts = new Map<string, number>();
      
      hands.forEach((hand: any) => {
        const label = handToLabel(hand);
        if (label) {
          handCounts.set(label, (handCounts.get(label) || 0) + 1);
          console.log(`Loaded hand: ${label} from ${hand.card1.rank}${hand.card1.suit} ${hand.card2.rank}${hand.card2.suit}`);
        }
      });
      
      // Only mark as selected if we have the complete set
      const labels = new Set<string>();
      handCounts.forEach((count, label) => {
        // Determine expected count
        let expectedCount = 0;
        if (label.length === 2) {
          // Pocket pair (AA, KK, etc.) - 6 combinations
          expectedCount = 6;
        } else if (label.endsWith('s')) {
          // Suited (AKs, etc.) - 4 combinations
          expectedCount = 4;
        } else if (label.endsWith('o')) {
          // Offsuit (AKo, etc.) - 12 combinations
          expectedCount = 12;
        }
        
        if (count >= expectedCount) {
          labels.add(label);
          console.log(`✓ ${label} is complete (${count}/${expectedCount})`);
        } else {
          console.log(`✗ ${label} is incomplete (${count}/${expectedCount})`);
        }
      });
      
      console.log(`Selected labels:`, Array.from(labels));
      setSelectedHands(labels);
    } catch (error) {
      console.error('Error loading range:', error);
      setError('Failed to load existing range');
    }
  };

  const handToLabel = (hand: any): string | null => {
    try {
      const r1 = hand.card1.rank;
      const r2 = hand.card2.rank;
      const s1 = hand.card1.suit;
      const s2 = hand.card2.suit;
      
      const rankMap: { [key: number]: string } = {
        14: 'A', 13: 'K', 12: 'Q', 11: 'J', 10: 'T',
        9: '9', 8: '8', 7: '7', 6: '6', 5: '5', 4: '4', 3: '3', 2: '2'
      };
      
      const a = rankMap[r1];
      const b = rankMap[r2];
      
      if (!a || !b) return null;
      
      // Pocket pair
      if (r1 === r2) return `${a}${a}`;
      
      // For non-pocket pairs, we need to figure out which grid cell this represents
      // The backend canonicalizes to have higher rank first
      const higherRank = Math.max(r1, r2);
      const lowerRank = Math.min(r1, r2);
      const higherChar = rankMap[higherRank];
      const lowerChar = rankMap[lowerRank];
      
      // Suited or offsuit?
      const suited = (s1 === s2);
      
      // The label is always higher rank first, then 's' or 'o'
      return `${higherChar}${lowerChar}${suited ? 's' : 'o'}`;
      
    } catch (e) {
      console.error('Error converting hand to label:', e, hand);
      return null;
    }
  };

  const getHandLabel = (i: number, j: number): string => {
    if (i === j) return `${ranks[i]}${ranks[i]}`;

    const rowValue = rankValues[i];
    const colValue = rankValues[j];
    const highChar = rowValue >= colValue ? ranks[i] : ranks[j];
    const lowChar = rowValue >= colValue ? ranks[j] : ranks[i];

    if (i < j) {
      return `${highChar}${lowChar}s`;
    }

    return `${highChar}${lowChar}o`;
  };

  const handleHandClick = async (i: number, j: number) => {
    const handLabel = getHandLabel(i, j);
    
    if (selectedHands.has(handLabel)) {
      setError('Hand already selected');
      setTimeout(() => setError(''), 2000);
      return;
    }

    const rank1 = rankValues[i];
    const rank2 = rankValues[j];
    let handType: string;

    if (i === j) {
      handType = 'pocket';
    } else if (i < j) {
      handType = 'suited';
    } else {
      handType = 'offsuit';
    }

    try {
      setLoading(true);
      setError('');
      
      console.log('Generating hands:', { type: handType, rank1, rank2, i, j });
      
      const genResponse = await axios.post('/api/hands/generate', {
        type: handType,
        rank1,
        rank2
      });

      console.log('Generated hands:', genResponse.data.hands.length);

      const addResponse = await axios.post(`/api/ranges/${rangeType}`, {
        hands: genResponse.data.hands
      });

      console.log('Added response:', addResponse.data);

      if (addResponse.data.added > 0) {
        const newSelected = new Set(selectedHands);
        newSelected.add(handLabel);
        setSelectedHands(newSelected);
        console.log('Updated selected hands:', Array.from(newSelected));
      }
    } catch (error: any) {
      console.error('Error adding hand:', error);
      setError(error.response?.data?.error || 'Failed to add hand');
    } finally {
      setLoading(false);
    }
  };

  const addAllHands = async () => {
    setLoading(true);
    setError('');
    
    try {
      const newLabels: string[] = [];
      let successCount = 0;
      let failCount = 0;
      
      for (let i = 0; i < rankValues.length; i++) {
        for (let j = 0; j < rankValues.length; j++) {
          const handLabel = getHandLabel(i, j);
          
          if (selectedHands.has(handLabel)) {
            continue;
          }
          
          const rank1 = rankValues[i];
          const rank2 = rankValues[j];
          let type: string;

          if (i === j) {
            type = 'pocket';
          } else if (i < j) {
            type = 'suited';
          } else {
            type = 'offsuit';
          }

          try {
            const gen = await axios.post('/api/hands/generate', { type, rank1, rank2 });
            const addResp = await axios.post(`/api/ranges/${rangeType}`, { hands: gen.data.hands });
            if (addResp.data.added > 0) {
              newLabels.push(handLabel);
              successCount++;
            }
          } catch (e: any) {
            console.error(`Failed to add ${handLabel}:`, e.response?.data || e.message);
            failCount++;
          }
        }
      }

      const newSelected = new Set([...selectedHands, ...newLabels]);
      setSelectedHands(newSelected);
      
      if (failCount > 0) {
        setError(`Added ${successCount} hands, ${failCount} failed`);
      }
    } catch (error: any) {
      console.error('Add all failed:', error);
      setError('Failed to add all hands');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Select Hands for {rangeType}</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        <div className="hand-info">
          Selected: {selectedHands.size} hand types
        </div>
        
        <div className="hand-grid-selector">
          {ranks.map((rank1, i) => (
            <div key={i} className="selector-row">
              {ranks.map((rank2, j) => {
                const label = getHandLabel(i, j);
                const isSelected = selectedHands.has(label);

                return (
                  <button
                    key={j}
                    className={`hand-button ${isSelected ? 'selected' : ''}`}
                    onClick={() => handleHandClick(i, j)}
                    disabled={isSelected || loading}
                    title={`${label} (${i === j ? 'pocket' : i < j ? 'suited' : 'offsuit'}) ${isSelected ? '✓' : ''}`}
                  >
                    {label}
                  </button>
                );
              })}
            </div>
          ))}
        </div>

        <div className="modal-footer">
          <button onClick={addAllHands} className="btn btn-success" disabled={loading}>
            {loading ? 'Adding...' : 'Add All Hands'}
          </button>
          <button onClick={onClose} className="btn btn-secondary" disabled={loading}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default HandSelector;