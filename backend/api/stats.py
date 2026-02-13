from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import Alert, Event
from core.services.geo import mock_geo_from_ip
from core.services.scoring import build_risk_snapshot

router = APIRouter(prefix="/stats", tags=["stats"])


def _resolve_cutoff(interval: str) -> datetime:
    now = datetime.utcnow()
    if interval == "1h":
        return now - timedelta(hours=1)
    if interval == "week":
        return now - timedelta(days=7)
    return now - timedelta(hours=24)


@router.get("")
async def get_stats(db: Session = Depends(get_db)):
    total_events = db.query(func.count(Event.id)).scalar() or 0
    windows_events = db.query(func.count(Event.id)).filter(Event.source_type == "windows").scalar() or 0
    syslog_events = db.query(func.count(Event.id)).filter(Event.source_type == "syslog").scalar() or 0
    all_devices = db.query(func.count(func.distinct(Event.device))).scalar() or 0
    return {
        "total_events": total_events,
        "windows_events": windows_events,
        "syslog_events": syslog_events,
        "all_devices": all_devices,
    }


@router.get("/timeline")
async def get_timeline(interval: str = Query("24h"), db: Session = Depends(get_db)):
    cutoff = _resolve_cutoff(interval)
    format_expr = "%Y-%m-%dT%H:%M" if interval in {"1h", "24h"} else "%Y-%m-%d"

    rows = (
        db.query(func.strftime(format_expr, Event.timestamp).label("bucket"), func.count(Event.id).label("events"))
        .filter(Event.timestamp >= cutoff)
        .group_by("bucket")
        .order_by("bucket")
        .all()
    )
    return [{"time": bucket, "events": count} for bucket, count in rows]


@router.get("/severity-breakdown")
async def severity_breakdown(db: Session = Depends(get_db)):
    rows = db.query(Alert.severity, func.count(Alert.id)).group_by(Alert.severity).all()
    result = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for severity, count in rows:
        result[severity] = count
    return result


@router.get("/top-ips")
async def top_ips(limit: int = Query(5, ge=1, le=50), db: Session = Depends(get_db)):
    snapshot = build_risk_snapshot(db, minutes=10)
    ranked = sorted(
        (
            {
                "ip": ip,
                "critical_count": data["critical_count"],
                "high_count": data["high_count"],
                "attack_score": data["risk_score"],
                "high_risk": data["high_risk"],
            }
            for ip, data in snapshot.items()
            if ip not in {"unknown", "127.0.0.1", "::1"}
        ),
        key=lambda item: (item["critical_count"], item["high_count"], item["attack_score"]),
        reverse=True,
    )
    return ranked[:limit]


@router.get("/dashboard")
async def dashboard(interval: str = Query("24h"), db: Session = Depends(get_db)):
    cutoff = _resolve_cutoff(interval)
    base_stats = await get_stats(db)

    severity_rows = (
        db.query(Alert.severity, func.count(Alert.id))
        .filter(Alert.timestamp >= cutoff)
        .group_by(Alert.severity)
        .all()
    )
    severity_distribution = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for severity, count in severity_rows:
        severity_distribution[severity] = count

    timeline_rows = (
        db.query(func.strftime("%Y-%m-%dT%H:%M", Alert.timestamp).label("bucket"), func.count(Alert.id).label("alerts"))
        .filter(Alert.timestamp >= cutoff)
        .group_by("bucket")
        .order_by("bucket")
        .all()
    )

    type_rows = (
        db.query(Alert.type, func.count(Alert.id).label("count"))
        .filter(Alert.timestamp >= cutoff)
        .group_by(Alert.type)
        .order_by(desc(func.count(Alert.id)))
        .all()
    )

    snapshot = build_risk_snapshot(db, minutes=10)
    top_attacking_ips = sorted(
        (
            {
                "ip": ip,
                "critical_count": data["critical_count"],
                "high_count": data["high_count"],
                "attack_score": data["risk_score"],
                "high_risk": data["high_risk"],
            }
            for ip, data in snapshot.items()
            if ip not in {"unknown", "127.0.0.1", "::1"}
        ),
        key=lambda item: (item["critical_count"], item["high_count"], item["attack_score"]),
        reverse=True,
    )[:5]

    geo_rows = []
    for row in top_attacking_ips:
        geo = mock_geo_from_ip(row["ip"])
        geo_rows.append(
            {
                "ip": row["ip"],
                "country": geo["country"],
                "city": geo["city"],
                "lat": geo["lat"],
                "lng": geo["lng"],
                "attack_score": row["attack_score"],
            }
        )

    recent_alerts = db.query(Alert).order_by(desc(Alert.timestamp)).limit(8).all()

    return {
        "stats": base_stats,
        "severity_distribution": severity_distribution,
        "attack_timeline": [{"time": bucket, "alerts": count} for bucket, count in timeline_rows],
        "attack_types": [{"type": name, "count": count} for name, count in type_rows],
        "top_attacking_ips": top_attacking_ips,
        "geo_sources": geo_rows,
        "recent_alerts": [
            {
                "id": row.id,
                "timestamp": row.timestamp.isoformat(),
                "ip": row.ip,
                "type": row.type,
                "severity": row.severity,
                "status": row.status,
                "description": row.description or "No description available.",
            }
            for row in recent_alerts
        ],
    }
