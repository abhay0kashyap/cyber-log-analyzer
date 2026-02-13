from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import Event, SystemConfig
from core.services.correlation import run_correlation_engine
from core.services.detector import detect_anomalies
from core.services.notifier import broadcast_ingest_updates
from core.services.parser import parse_log_content

router = APIRouter(prefix="/logs", tags=["logs"])


def _live_enabled(db: Session) -> bool:
    state = db.get(SystemConfig, 1)
    return True if state is None else state.live_monitoring


@router.post("/upload")
async def upload_log(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    raw_content = (await file.read()).decode("utf-8", errors="ignore")
    parsed = parse_log_content(raw_content, filename=file.filename)
    if not parsed:
        return {"ingested_events": 0, "generated_alerts": 0, "filename": file.filename, "correlated_alerts": 0}

    events: list[Event] = []
    for row in parsed:
        event = Event(**row)
        db.add(event)
        events.append(event)

    db.commit()
    for event in events:
        db.refresh(event)

    anomaly_alerts = detect_anomalies(db, events) if _live_enabled(db) else []
    correlated_alerts = run_correlation_engine(db) if _live_enabled(db) else []
    generated_alerts = [*anomaly_alerts, *correlated_alerts]

    await broadcast_ingest_updates(db, events[-1], generated_alerts)

    return {
        "ingested_events": len(events),
        "generated_alerts": len(generated_alerts),
        "correlated_alerts": len(correlated_alerts),
        "filename": file.filename,
    }
