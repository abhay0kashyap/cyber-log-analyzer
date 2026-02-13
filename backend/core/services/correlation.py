from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from core.models import Alert


def _has_recent_correlated_alert(db: Session, ip: str, cutoff: datetime) -> bool:
    return (
        db.query(Alert)
        .filter(Alert.ip == ip, Alert.type == "correlated_attack", Alert.timestamp >= cutoff)
        .first()
        is not None
    )


def run_correlation_engine(db: Session, window_seconds: int = 120) -> list[Alert]:
    now = datetime.utcnow()
    cutoff = now - timedelta(seconds=window_seconds)

    rows = (
        db.query(Alert)
        .filter(
            Alert.timestamp >= cutoff,
            Alert.type.in_(["brute_force", "malware_detection"]),
        )
        .all()
    )

    grouped: dict[str, dict[str, int]] = defaultdict(lambda: {"brute_force": 0, "malware_detection": 0})
    for row in rows:
        grouped[row.ip][row.type] += 1

    created: list[Alert] = []
    for ip, counts in grouped.items():
        if counts["brute_force"] < 3 or counts["malware_detection"] < 1:
            continue
        if _has_recent_correlated_alert(db, ip, cutoff):
            continue

        created.append(
            Alert(
                timestamp=now,
                ip=ip,
                type="correlated_attack",
                severity="Critical",
                status="New",
                description=(
                    "Correlation rule matched: 3+ brute_force and 1+ malware_detection "
                    f"from {ip} within 2 minutes."
                ),
            )
        )

    if created:
        db.add_all(created)
        db.commit()
        for item in created:
            db.refresh(item)

    return created
