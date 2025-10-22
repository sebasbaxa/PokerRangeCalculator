# Poker Range Calculator

A graphical tool built in Python to calculate and visualize win rates between different poker hand ranges in Texas Hold'em.

## Features

- **Interactive Hand Selection**: Visual grid interface for selecting poker hands
  - Click individual hands or drag to select multiple hands
  - "Add All Hands" button for quick full range selection
  - Suited and offsuit hands clearly distinguished
  - Pocket pairs easily identifiable

- **Real-time Win Rate Calculation**
  - Monte Carlo simulation for win rate estimation
  - Configurable number of simulations per hand
  - Color-coded results for easy interpretation:
    - Green: >80% win rate
    - Orange: >60% win rate
    - Yellow: >45% win rate
    - White: ≤45% win rate

- **Range Management**
  - Separate hero and villain range selection
  - Reset functionality to clear all selections
  - Persistent range storage during session

## How It Works

The calculator uses Monte Carlo simulation to determine win rates:
1. For each hand in the hero's range, it runs multiple simulations against random hands from the villain's range
2. Each simulation generates a random board and evaluates both hands
3. Results are aggregated to calculate the win percentage for each hero hand
4. The grid display updates in real-time with color-coding based on win rates

## Usage

1. Select "Ranges" from the menu bar
   - Choose "Hero Range" to select your hands
   - Choose "Villain Range" to select opponent's range

2. Adjust simulation settings (optional)
   - Navigate to "Simulation" in the menu
   - Set the number of simulations per hand

3. Click "Run Calculation" to start the analysis

4. Interpret results in the main grid:
   - Each cell shows the hand and its win rate
   - Colors indicate strength against the villain range
   - Higher percentages indicate stronger hands

## Requirements

- Python 3.x
- tkinter (usually comes with Python)
