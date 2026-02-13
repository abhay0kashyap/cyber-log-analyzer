from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Response
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import Alert, Event
from core.services.scoring import build_risk_snapshot

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/download")
async def download_report(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    day_ago = now - timedelta(hours=24)

    total_events = db.query(func.count(Event.id)).scalar() or 0
    total_alerts = db.query(func.count(Alert.id)).scalar() or 0

    severity_rows = db.query(Alert.severity, func.count(Alert.id)).group_by(Alert.severity).all()
    severity_distribution = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for severity, count in severity_rows:
        severity_distribution[severity] = count

    timeline_rows = (
        db.query(func.strftime("%Y-%m-%dT%H:%M", Event.timestamp), func.count(Event.id))
        .filter(Event.timestamp >= day_ago)
        .group_by(func.strftime("%Y-%m-%dT%H:%M", Event.timestamp))
        .order_by(func.strftime("%Y-%m-%dT%H:%M", Event.timestamp))
        .all()
    )

    type_rows = (
        db.query(Alert.type, func.count(Alert.id).label("count"))
        .group_by(Alert.type)
        .order_by(desc(func.count(Alert.id)))
        .all()
    )

    risk_snapshot = build_risk_snapshot(db, minutes=10)
    top_ip_sources = sorted(
        (
            {
                "ip": ip,
                "count": data["total_alerts"],
                "attack_score": data["risk_score"],
                "high_risk": data["high_risk"],
            }
            for ip, data in risk_snapshot.items()
        ),
        key=lambda item: (item["attack_score"], item["count"]),
        reverse=True,
    )[:10]

    latest_alerts = db.query(Alert).order_by(desc(Alert.timestamp)).limit(200).all()

    return {
        "generated_at": now.isoformat(),
        "summary": {
            "total_events": total_events,
            "total_alerts": total_alerts,
            "critical_alerts": severity_distribution["Critical"],
            "high_alerts": severity_distribution["High"],
        },
        "severity_distribution": severity_distribution,
        "events_over_time": [{"time": t, "events": c} for t, c in timeline_rows],
        "attack_types": [{"type": t, "count": c} for t, c in type_rows],
        "top_ip_sources": top_ip_sources,
        "alerts": [
            {
                "id": a.id,
                "timestamp": a.timestamp.isoformat(),
                "ip": a.ip,
                "type": a.type,
                "severity": a.severity,
                "status": a.status,
                "description": a.description or "No description available.",
            }
            for a in latest_alerts
        ],
    }


@router.get("/download.csv")
async def download_report_csv(db: Session = Depends(get_db)):
    rows = db.query(Alert).order_by(desc(Alert.timestamp)).limit(1000).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "timestamp", "ip", "type", "severity", "status", "blocked", "description"])
    for row in rows:
        writer.writerow(
            [
                row.id,
                row.timestamp.isoformat(),
                row.ip,
                row.type,
                row.severity,
                row.status,
                row.blocked,
                row.description or "No description available.",
            ]
        )

    content = output.getvalue()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=cyber-report-{datetime.utcnow().date()}.csv"},
    )
