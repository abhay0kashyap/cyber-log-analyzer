# Cyber Log Analyzer / Mini-SIEM

Modern SOC-style dashboard for log ingestion, anomaly detection, alert correlation, risk scoring, and incident triage.

## Stack
- Frontend: React + Vite + Tailwind CSS + Recharts + Axios
- Backend: FastAPI + SQLAlchemy + SQLite
- Realtime strategy: polling every 5 seconds (plus optional websocket support at `/ws/live`)

## Architecture

```text
backend/
  main.py
  ws.py
  requirements.txt
  api/
    stats.py
    alerts.py
    logs.py
    reports.py
    settings.py
  core/
    database.py
    schemas.py
    models.py
    services/
      parser.py
      detector.py
      correlation.py
      scoring.py
      geo.py
      notifier.py
  scripts/
    seed_demo_logs.py

frontend/src/
  components/
    Sidebar.jsx
    Navbar.jsx
    StatCard.jsx
    EventChart.jsx
    AlertTable.jsx
    ReportSummary.jsx
    ThresholdEditor.jsx
    AlertDetailModal.jsx
    TopAttackingIps.jsx
    GeoThreatMap.jsx
  pages/
    Dashboard.jsx
    Alerts.jsx
    Reports.jsx
    Settings.jsx
  hooks/
    useDebouncedValue.js
  services/
    api.js
  utils/
    severity.js
  App.jsx
  main.jsx
  index.css
```

## Features

### Detection Rules
- Brute Force: failed attempts from same IP exceed threshold -> `High`
- Failed Login Spike: repeated failed logins exceed threshold -> `Medium`
- Unknown IP Spike: unusual activity spike from IP -> `Medium`
- Malware Signature Pattern -> `Critical`

### Correlation Engine
If same IP triggers:
- 3+ `brute_force`
- and 1+ `malware_detection`
within 2 minutes,
then create:
- `type=correlated_attack`
- `severity=Critical`

### Risk Scoring
- Critical = 10
- High = 7
- Medium = 4
- Low = 1

Risk score is computed per IP over last 10 minutes.
If score > 25 -> marked as `HIGH RISK`.

### SOC Dashboard
- Attack timeline chart
- Severity distribution
- Attack type pie chart
- Top attacking IPs with risk score
- Geo threat feed (mocked geolocation)
- Recent alerts list
- Real log upload and parsing

### Alerts Workflow
- Instant filters (severity/status/search)
- Pagination
- Debounced search input
- Alert status transitions: `New`, `Investigating`, `Resolved`
- Auto-block simulation endpoint
- Alert detail modal payload includes related logs, related alerts, risk, and timeline

## API Endpoints
- `GET /` -> API status message
- `GET /health`
- `GET /stats`
- `GET /stats/dashboard?interval=1h|24h|week`
- `GET /stats/timeline?interval=1h|24h|week`
- `GET /stats/severity-breakdown`
- `GET /stats/top-ips`
- `GET /alerts?page=1&page_size=15&severity=&status=&ip=&q=`
- `GET /alerts/{id}`
- `PATCH /alerts/{id}/status`
- `POST /alerts/{id}/block`
- `POST /logs/upload`
- `GET /reports/download`
- `GET /reports/download.csv`
- `GET /settings`
- `POST /settings`
- `WS /ws/live`

## Run Locally

### Backend
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173` (or next free port)

### Seed Demo Data
```bash
source .venv/bin/activate
cd backend
python scripts/seed_demo_logs.py
```
