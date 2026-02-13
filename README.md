# Cyber Log Analyzer (Mini-SIEM)

A lightweight SOC-style application for log ingestion, anomaly detection, alert triage, and reporting.

## Tech Stack
- Backend: FastAPI, SQLAlchemy, SQLite
- Frontend: React, Vite, Tailwind CSS, Recharts, Axios
- Realtime: Dashboard polling every 5 seconds and optional websocket updates at `WS /ws/live`

## Key Features
- Log upload and parsing (`POST /logs/upload`)
- Detection rules for brute force, failed-login spikes, unknown-IP spikes, and malware signatures
- Alert correlation engine (escalates combined attack patterns to critical alerts)
- Risk scoring per source IP over a rolling 10-minute window
- Alert workflow with status transitions: `New`, `Investigating`, `Resolved`
- Simulated firewall block action from alert detail (`POST /alerts/{id}/block`)
- Dashboard views: timeline, severity breakdown, attack types, top IPs, geo feed, and recent alerts
- JSON and CSV report export

## Repository Layout

```text
backend/
  main.py
  ws.py
  requirements.txt
  api/
  core/
  scripts/

frontend/
  src/
  package.json

docker-compose.yml
README.md
```

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1) Run Backend
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend URLs:
- API root: `http://127.0.0.1:8000`
- OpenAPI docs: `http://127.0.0.1:8000/docs`

### 2) Run Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend URL:
- App: `http://127.0.0.1:5173`

### 3) Seed Demo Data (Optional)
```bash
source .venv/bin/activate
cd backend
python scripts/seed_demo_logs.py
```

## Docker

Run both services with Docker Compose:

```bash
docker compose up --build
```

Default ports:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

Stop services:

```bash
docker compose down
```

## Configuration Notes
- Frontend API URL can be overridden with `VITE_API_URL`. Default is `http://127.0.0.1:8000`.
- Backend database path defaults to `backend/data/cyber_log_analyzer.db`.
- You can override DB location with `DATABASE_URL` (for example in Docker or shell env).

## API Endpoints
- `GET /`
- `GET /health`
- `GET /stats`
- `GET /stats/dashboard?interval=1h|24h|week`
- `GET /stats/timeline?interval=1h|24h|week`
- `GET /stats/severity-breakdown`
- `GET /stats/top-ips?limit=5`
- `GET /alerts?page=1&page_size=20&severity=&status=&ip=&q=`
- `GET /alerts/{id}`
- `PATCH /alerts/{id}/status`
- `POST /alerts/{id}/block`
- `POST /logs/upload`
- `GET /reports/download`
- `GET /reports/download.csv`
- `GET /settings`
- `POST /settings`
- `WS /ws/live`
