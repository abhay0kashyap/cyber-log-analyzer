from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import Alert, BlockedIP, Event
from core.schemas import AlertListResponse, AlertStatusUpdate
from core.services.geo import mock_geo_from_ip
from core.services.scoring import build_risk_snapshot

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _serialize_alert(row: Alert, risk_snapshot: dict[str, dict]) -> dict:
    risk = risk_snapshot.get(row.ip, {"risk_score": 0, "high_risk": False})
    return {
        "id": row.id,
        "timestamp": row.timestamp.isoformat(),
        "ip": row.ip,
        "type": row.type,
        "severity": row.severity,
        "description": row.description or "No description available.",
        "status": row.status or "New",
        "blocked": bool(getattr(row, "blocked", False)),
        "risk_score": risk["risk_score"],
        "high_risk": risk["high_risk"],
        "geo": mock_geo_from_ip(row.ip),
    }


@router.get("", response_model=AlertListResponse)
async def get_alerts(
    severity: str | None = Query(None),
    ip: str | None = Query(None),
    status: str | None = Query(None),
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=5, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Alert)

    if ip:
        query = query.filter(Alert.ip.contains(ip))
    if status:
        query = query.filter(Alert.status == status)
    if q:
        query = query.filter(or_(Alert.ip.contains(q), Alert.type.contains(q), Alert.description.contains(q)))
    if severity:
        query = query.filter(Alert.severity == severity)

    total = query.count()
    total_pages = max((total + page_size - 1) // page_size, 1)

    rows = (
        query.order_by(desc(Alert.timestamp)).offset((page - 1) * page_size).limit(page_size).all()
    )

    severity_rows = query.with_entities(Alert.severity, func.count(Alert.id)).group_by(Alert.severity).all()
    severity_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for sev, count in severity_rows:
        severity_counts[sev] = count

    risk_snapshot = build_risk_snapshot(db, minutes=10)

    return {
        "items": [_serialize_alert(row, risk_snapshot) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "severity_counts": severity_counts,
    }


@router.get("/{alert_id}")
async def get_alert_detail(alert_id: int, db: Session = Depends(get_db)):
    row = db.get(Alert, alert_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    risk_snapshot = build_risk_snapshot(db, minutes=10)
    risk_data = risk_snapshot.get(row.ip, {"risk_score": 0, "high_risk": False})

    related_logs = (
        db.query(Event)
        .filter(Event.ip == row.ip)
        .order_by(desc(Event.timestamp))
        .limit(40)
        .all()
    )

    related_alerts = (
        db.query(Alert)
        .filter(Alert.ip == row.ip)
        .order_by(desc(Alert.timestamp))
        .limit(20)
        .all()
    )

    two_hours = datetime.utcnow() - timedelta(hours=2)
    timeline_rows = (
        db.query(func.strftime("%Y-%m-%dT%H:%M", Event.timestamp).label("bucket"), func.count(Event.id).label("events"))
        .filter(Event.ip == row.ip, Event.timestamp >= two_hours)
        .group_by("bucket")
        .order_by("bucket")
        .all()
    )

    blocked_rows = (
        db.query(BlockedIP).filter(BlockedIP.ip == row.ip).order_by(desc(BlockedIP.created_at)).limit(5).all()
    )

    return {
        "alert": _serialize_alert(row, risk_snapshot),
        "risk_score": risk_data["risk_score"],
        "high_risk": risk_data["high_risk"],
        "related_logs": [
            {
                "id": item.id,
                "timestamp": item.timestamp.isoformat(),
                "source_type": item.source_type,
                "event_type": item.event_type,
                "status": item.status,
                "raw": item.raw,
            }
            for item in related_logs
        ],
        "related_alerts": [
            {
                "id": item.id,
                "timestamp": item.timestamp.isoformat(),
                "type": item.type,
                "severity": item.severity,
                "status": item.status,
                "description": item.description or "No description available.",
            }
            for item in related_alerts
        ],
        "activity_timeline": [{"time": bucket, "events": events} for bucket, events in timeline_rows],
        "blocked_history": [
            {
                "id": item.id,
                "timestamp": item.created_at.isoformat(),
                "reason": item.reason,
            }
            for item in blocked_rows
        ],
    }


@router.patch("/{alert_id}/status")
async def update_alert_status(alert_id: int, payload: AlertStatusUpdate, db: Session = Depends(get_db)):
    row = db.get(Alert, alert_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    row.status = payload.status
    db.commit()
    db.refresh(row)

    return {
        "id": row.id,
        "status": row.status,
        "updated_at": datetime.utcnow().isoformat(),
    }


@router.post("/{alert_id}/block")
async def block_ip(alert_id: int, db: Session = Depends(get_db)):
    row = db.get(Alert, alert_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    row.blocked = True
    if row.status == "New":
        row.status = "Investigating"

    blocked_record = BlockedIP(
        ip=row.ip,
        reason=f"Simulated firewall block from alert #{row.id}",
        source_alert_id=row.id,
    )
    db.add(blocked_record)
    db.commit()
    db.refresh(row)
    db.refresh(blocked_record)

    return {
        "alert_id": row.id,
        "ip": row.ip,
        "blocked": True,
        "blocked_at": blocked_record.created_at.isoformat(),
        "message": f"Firewall block simulated for {row.ip}",
    }
