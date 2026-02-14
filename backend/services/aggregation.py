from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Alert, Event

SUPPORTED_RANGES = {"1h", "24h", "week"}


def resolve_cutoff(range_key: str) -> datetime:
    now = datetime.utcnow()
    if range_key == "1h":
        return now - timedelta(hours=1)
    if range_key == "week":
        return now - timedelta(days=7)
    return now - timedelta(hours=24)


def _timeline_bucket_format(range_key: str) -> str:
    if range_key == "1h":
        return "%Y-%m-%dT%H:%M"
    return "%Y-%m-%dT%H:00"


def get_metrics(db: Session, range_key: str) -> dict:
    if range_key not in SUPPORTED_RANGES:
        range_key = "24h"

    cutoff = resolve_cutoff(range_key)
    timeline_fmt = _timeline_bucket_format(range_key)

    event_query = db.query(Event).filter(Event.timestamp >= cutoff)
    alert_query = db.query(Alert).filter(Alert.timestamp >= cutoff)

    total_events = event_query.count()
    windows_events = event_query.filter(Event.source == "windows").count()
    syslog_events = event_query.filter(Event.source == "syslog").count()
    devices = db.query(func.count(func.distinct(Event.hostname))).filter(Event.timestamp >= cutoff).scalar() or 0

    severity = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    severity_rows = (
        db.query(Alert.severity, func.count(Alert.id))
        .filter(Alert.timestamp >= cutoff)
        .group_by(Alert.severity)
        .all()
    )
    for sev, count in severity_rows:
        key = str(sev).lower()
        if key in severity:
            severity[key] = count

    timeline_rows = (
        db.query(
            func.strftime(timeline_fmt, Event.timestamp).label("bucket"),
            func.count(Event.id).label("count"),
        )
        .filter(Event.timestamp >= cutoff)
        .group_by("bucket")
        .order_by("bucket")
        .all()
    )
    attack_timeline = [{"timestamp": bucket, "count": count} for bucket, count in timeline_rows]

    top_ip_rows = (
        db.query(Event.ip, func.count(Event.id).label("count"))
        .filter(Event.timestamp >= cutoff, Event.ip != "unknown")
        .group_by(Event.ip)
        .order_by(func.count(Event.id).desc())
        .limit(10)
        .all()
    )
    top_ips = [{"ip": ip, "count": count} for ip, count in top_ip_rows]

    recent_activity = db.query(Event.id).filter(Event.timestamp >= datetime.utcnow() - timedelta(minutes=10)).first() is not None

    recent_alert_rows = (
        db.query(Alert)
        .filter(Alert.timestamp >= cutoff)
        .order_by(Alert.timestamp.desc())
        .limit(20)
        .all()
    )
    recent_alerts = [
        {
            "id": row.id,
            "type": row.type,
            "severity": row.severity,
            "ip": row.ip,
            "timestamp": row.timestamp.isoformat(),
            "message": row.message,
        }
        for row in recent_alert_rows
    ]

    return {
        "total_events": total_events,
        "windows_events": windows_events,
        "syslog_events": syslog_events,
        "devices": devices,
        "severity_distribution": severity,
        "attack_timeline": attack_timeline,
        "top_ips": top_ips,
        "recent_activity": recent_activity,
        "recent_alerts": recent_alerts,
    }


def get_alerts_for_range(db: Session, range_key: str) -> list[dict]:
    cutoff = resolve_cutoff(range_key)
    rows = (
        db.query(Alert)
        .filter(Alert.timestamp >= cutoff)
        .order_by(Alert.timestamp.desc())
        .all()
    )
    return [
        {
            "id": row.id,
            "type": row.type,
            "severity": row.severity,
            "ip": row.ip,
            "timestamp": row.timestamp.isoformat(),
            "message": row.message,
        }
        for row in rows
    ]


def get_top_ips_for_range(db: Session, range_key: str, limit: int = 20) -> list[dict]:
    cutoff = resolve_cutoff(range_key)
    rows = (
        db.query(Event.ip, func.count(Event.id).label("count"))
        .filter(Event.timestamp >= cutoff, Event.ip != "unknown")
        .group_by(Event.ip)
        .order_by(func.count(Event.id).desc())
        .limit(limit)
        .all()
    )
    return [{"ip": ip, "count": count} for ip, count in rows]

