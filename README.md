# Poker Range Calculator

Visualize Texas Hold'em preflop ranges and estimate equity via Monte Carlo simulations.

## Features

- Interactive 13×13 range grid with suited/offsuit/pairs
- Live progress via Server-Sent Events (SSE)
- Persisted ranges (SQLite via Flask + SQLAlchemy)
- React + Vite + TypeScript frontend

## Quick Start (Docker)

Prerequisites:
- Docker Desktop (Windows) with Linux containers
- Docker Compose

1) Build and start services
```powershell
cd c:\Projects\PokerProject
docker compose up --build
```

2) Access the app
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

The backend database is persisted in the Compose volume (backend-data) and stored at /app/instance/poker.db inside the container.

## Project Structure

- backend: Flask API, SQLAlchemy models, simulation engine
- frontend: React/Vite app, range selector, results grid
- docker-compose.yml: Orchestrates backend + frontend
- Dockerfiles: Container definitions for backend and frontend


## Manual Run (Optional)

If not using Docker:
```powershell
# Backend
cd c:\Projects\PokerProject\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app main run --host 127.0.0.1 --port 5000

# Frontend (new terminal)
cd c:\Projects\PokerProject\frontend
npm install
npm run dev
```