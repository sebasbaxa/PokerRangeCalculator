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