from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from core.models import Alert

SEVERITY_SCORES = {
    "Critical": 10,
    "High": 7,
    "Medium": 4,
    "Low": 1,
}


def score_for_severity(severity: str) -> int:
    return SEVERITY_SCORES.get(severity, 0)


def build_risk_snapshot(db: Session, minutes: int = 10) -> dict[str, dict]:
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    rows = db.query(Alert).filter(Alert.timestamp >= cutoff).all()

    snapshot: dict[str, dict] = defaultdict(
        lambda: {
            "risk_score": 0,
            "high_risk": False,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "total_alerts": 0,
        }
    )

    for row in rows:
        bucket = snapshot[row.ip]
        bucket["risk_score"] += score_for_severity(row.severity)
        bucket["total_alerts"] += 1

        if row.severity == "Critical":
            bucket["critical_count"] += 1
        elif row.severity == "High":
            bucket["high_count"] += 1
        elif row.severity == "Medium":
            bucket["medium_count"] += 1
        elif row.severity == "Low":
            bucket["low_count"] += 1

    for data in snapshot.values():
        data["high_risk"] = data["risk_score"] > 25

    return snapshot
