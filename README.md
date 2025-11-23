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

## Architecture

| Layer    | Tech                                     | Notes                                   |
|----------|------------------------------------------|-----------------------------------------|
| Frontend | React, TypeScript, Vite, Axios           | Renders grids, modals, and SSE listener |
| Backend  | Flask, SQLAlchemy, SQLite                | Manages ranges, simulations, SSE stream |
| Simulation | Custom Python engine                    | Builds random boards, evaluates winners |

## Prerequisites

- Node.js 18+
- Python 3.11+
- PowerShell (for the commands below)

## Setup

1. **Install frontend dependencies**
   ```powershell
   cd c:\Projects\PokerProject\frontend
   npm install
   ```

2. **Create and activate a Python virtual environment**
   ```powershell
   cd c:\Projects\PokerProject\backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install backend dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **(Optional) Seed fresh database**
   ```powershell
   Remove-Item .\instance\poker.db -ErrorAction SilentlyContinue
   ```

## Running the app

1. **Backend**
   ```powershell
   cd c:\Projects\PokerProject\backend
   .\.venv\Scripts\Activate.ps1
   flask --app main run --host 127.0.0.1 --port 5000
   ```

2. **Frontend (new terminal)**
   ```powershell
   cd c:\Projects\PokerProject\frontend
   npm run dev
   ```

3. Open the Vite URL (default `http://127.0.0.1:5173/`).

## Usage tips

- Add ranges via **Hero Range** / **Villain Range** buttons.
- Use **Simulation Settings** to adjust trials per hand.
- Click **Run Calculation** to stream live results.
- Reset ranges with the **Reset Ranges** button in the footer.

