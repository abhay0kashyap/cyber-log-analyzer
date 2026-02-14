from __future__ import annotations

import json
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, Query, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import Event
from services.aggregation import get_alerts_for_range, get_metrics, get_top_ips_for_range
from services.detection import run_detection
from services.geo import build_geo_feed
from services.parser import parse_log_content

try:
    from api.alerts import router as legacy_alerts_router
    from api.logs import router as legacy_logs_router
    from api.reports import router as legacy_reports_router
    from api.settings import router as legacy_settings_router
    from api.stats import router as legacy_stats_router
    from core.database import init_db as init_legacy_db
except Exception:  # pragma: no cover - keeps API alive if legacy modules are unavailable
    legacy_alerts_router = None
    legacy_logs_router = None
    legacy_reports_router = None
    legacy_settings_router = None
    legacy_stats_router = None
    init_legacy_db = None


class WebSocketManager:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._clients.discard(websocket)

    async def broadcast(self, payload: dict) -> None:
        if not self._clients:
            return

        encoded = json.dumps(payload)
        stale: list[WebSocket] = []
        for client in self._clients:
            try:
                await client.send_text(encoded)
            except Exception:
                stale.append(client)

        for client in stale:
            self.disconnect(client)


ws_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    if init_legacy_db is not None:
        init_legacy_db()
    yield


app = FastAPI(title="Cyber Log Analyzer API", version="4.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if legacy_stats_router is not None:
    app.include_router(legacy_stats_router)
if legacy_alerts_router is not None:
    app.include_router(legacy_alerts_router)
if legacy_logs_router is not None:
    app.include_router(legacy_logs_router)
if legacy_reports_router is not None:
    app.include_router(legacy_reports_router)
if legacy_settings_router is not None:
    app.include_router(legacy_settings_router)


@app.get("/")
async def root() -> dict:
    return {"message": "Cyber Log Analyzer API running"}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/metrics")
async def api_metrics(
    range: str = Query("24h", pattern="^(1h|24h|week)$"),
    db: Session = Depends(get_db),
) -> dict:
    return get_metrics(db, range)


@app.get("/api/alerts")
async def api_alerts(
    range: str = Query("24h", pattern="^(1h|24h|week)$"),
    db: Session = Depends(get_db),
) -> dict:
    return {"alerts": get_alerts_for_range(db, range)}


@app.get("/api/geo-feed")
async def api_geo_feed(
    range: str = Query("24h", pattern="^(1h|24h|week)$"),
    db: Session = Depends(get_db),
) -> dict:
    top_ips = get_top_ips_for_range(db, range, limit=20)
    return {"records": build_geo_feed(db, top_ips)}


async def _process_upload(file: UploadFile, db: Session) -> dict:
    content = (await file.read()).decode("utf-8", errors="ignore")
    parsed_rows = parse_log_content(content)

    if not parsed_rows:
        metrics = get_metrics(db, "24h")
        return {
            "ingested_events": 0,
            "generated_alerts": 0,
            "new_alerts": [],
            "metrics": metrics,
        }

    events = [
        Event(
            timestamp=row["timestamp"],
            source=row["source"],
            hostname=row["hostname"],
            ip=row["ip"],
            raw_log=row["raw_log"],
        )
        for row in parsed_rows
    ]

    db.add_all(events)
    db.commit()
    for event in events:
        db.refresh(event)

    new_alerts = run_detection(db, events)

    top_ips = get_top_ips_for_range(db, "24h", limit=20)
    build_geo_feed(db, top_ips)
    metrics = get_metrics(db, "24h")

    await ws_manager.broadcast({"type": "metrics_update"})

    return {
        "ingested_events": len(events),
        "generated_alerts": len(new_alerts),
        "new_alerts": [
            {
                "id": alert.id,
                "type": alert.type,
                "severity": alert.severity,
                "ip": alert.ip,
                "timestamp": alert.timestamp.isoformat(),
                "message": alert.message,
            }
            for alert in new_alerts
        ],
        "metrics": metrics,
    }


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    return await _process_upload(file, db)


# Backward-compatible alias for older clients.
@app.post("/upload")
async def upload_alias(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    return await _process_upload(file, db)


@app.websocket("/ws/updates")
async def ws_updates(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
