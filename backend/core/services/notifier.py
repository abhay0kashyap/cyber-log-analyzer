from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from core.models import Alert, Event
from core.services.scoring import build_risk_snapshot
from ws import ws_manager


async def broadcast_ingest_updates(db: Session, latest_event: Event, new_alerts: list[Alert]) -> None:
    total_events = db.query(func.count(Event.id)).scalar() or 0

    await ws_manager.broadcast(
        {
            "channel": "event",
            "timestamp": latest_event.timestamp.isoformat(),
            "event_count": total_events,
            "source_type": latest_event.source_type,
            "ip": latest_event.ip,
            "status": latest_event.status,
        }
    )

    if not new_alerts:
        return

    risk_snapshot = build_risk_snapshot(db, minutes=10)
    for alert in new_alerts:
        risk = risk_snapshot.get(alert.ip, {"risk_score": 0, "high_risk": False})
        await ws_manager.broadcast(
            {
                "channel": "alert",
                "id": alert.id,
                "timestamp": alert.timestamp.isoformat(),
                "ip": alert.ip,
                "type": alert.type,
                "severity": alert.severity,
                "description": alert.description,
                "status": alert.status,
                "risk_score": risk["risk_score"],
                "high_risk": risk["high_risk"],
            }
        )
