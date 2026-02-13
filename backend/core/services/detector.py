from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from core.models import Alert, Event, RuleConfig

DEFAULT_THRESHOLDS = {
    "brute_force_count": 10,
    "repeated_failed_threshold": 5,
    "unknown_ip_spike_threshold": 15,
}

MALWARE_SIGNATURES = [
    "mimikatz",
    "powershell -enc",
    "ransomware",
    "trojan",
    "meterpreter",
    "cobalt strike",
    "malware",
]


def get_thresholds(db: Session) -> dict[str, int]:
    values = {row.key: row.value for row in db.query(RuleConfig).all()}
    merged = DEFAULT_THRESHOLDS.copy()
    merged.update(values)
    return merged


def save_thresholds(db: Session, payload: dict[str, int]) -> dict[str, int]:
    for key, default_val in DEFAULT_THRESHOLDS.items():
        value = int(payload.get(key, default_val))
        record = db.get(RuleConfig, key)
        if record:
            record.value = value
        else:
            db.add(RuleConfig(key=key, value=value))
    db.commit()
    return get_thresholds(db)


def _recent_duplicate_exists(db: Session, alert_type: str, ip: str, seconds: int = 90) -> bool:
    cutoff = datetime.utcnow() - timedelta(seconds=seconds)
    return (
        db.query(Alert)
        .filter(Alert.type == alert_type, Alert.ip == ip, Alert.timestamp >= cutoff)
        .first()
        is not None
    )


def detect_anomalies(db: Session, new_events: list[Event]) -> list[Alert]:
    if not new_events:
        return []

    thresholds = get_thresholds(db)
    alerts: list[Alert] = []
    now = datetime.utcnow()
    ten_min_cutoff = now - timedelta(minutes=10)

    failed_new = Counter()
    new_ip_events = Counter()

    for event in new_events:
        ip = event.ip or "unknown"
        new_ip_events[ip] += 1

        if event.status.lower() == "failed":
            failed_new[ip] += 1

        raw_lower = (event.raw or "").lower()
        if any(sig in raw_lower for sig in MALWARE_SIGNATURES):
            if not _recent_duplicate_exists(db, "malware_detection", ip, seconds=30):
                alerts.append(
                    Alert(
                        timestamp=now,
                        ip=ip,
                        type="malware_detection",
                        severity="Critical",
                        status="New",
                        description=f"Malware signature pattern detected in log payload from {ip}.",
                    )
                )

    for ip in failed_new:
        failed_count = (
            db.query(Event)
            .filter(Event.ip == ip, Event.status == "failed", Event.timestamp >= ten_min_cutoff)
            .count()
        )
        if failed_count >= thresholds["brute_force_count"]:
            if not _recent_duplicate_exists(db, "brute_force", ip, seconds=20):
                alerts.append(
                    Alert(
                        timestamp=now,
                        ip=ip,
                        type="brute_force",
                        severity="High",
                        status="New",
                        description=f"Brute force detected from {ip}: {failed_count} failed attempts.",
                    )
                )
        elif failed_count >= thresholds["repeated_failed_threshold"]:
            if not _recent_duplicate_exists(db, "failed_login_spike", ip):
                alerts.append(
                    Alert(
                        timestamp=now,
                        ip=ip,
                        type="failed_login_spike",
                        severity="Medium",
                        status="New",
                        description=f"Failed login spike for {ip}: {failed_count} failed logins.",
                    )
                )

    for ip in new_ip_events:
        if ip in {"unknown", "127.0.0.1", "::1"}:
            continue
        recent_activity = db.query(Event).filter(Event.ip == ip, Event.timestamp >= ten_min_cutoff).count()
        if recent_activity >= thresholds["unknown_ip_spike_threshold"] and not _recent_duplicate_exists(
            db, "unknown_ip_spike", ip
        ):
            alerts.append(
                Alert(
                    timestamp=now,
                    ip=ip,
                    type="unknown_ip_spike",
                    severity="Medium",
                    status="New",
                    description=f"Unknown IP spike detected for {ip}: {recent_activity} events in 10 minutes.",
                )
            )

    if alerts:
        db.add_all(alerts)
        db.commit()
        for alert in alerts:
            db.refresh(alert)

    return alerts
