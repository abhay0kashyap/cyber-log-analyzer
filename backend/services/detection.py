from __future__ import annotations

import ipaddress
from datetime import datetime, timedelta

from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.models import Alert, Event

BRUTE_FORCE_THRESHOLD = 5
REPEATED_FAILED_THRESHOLD = 3
UNKNOWN_IP_SPIKE_THRESHOLD = 50
WINDOW_MINUTES = 10

FAILED_KEYWORDS = ("failed password", "authentication failure", "login failed", "logon failure")
MALWARE_KEYWORDS = ("malware", "ransomware", "trojan", "mimikatz", "meterpreter", "cobalt strike")

SEVERITY_MAP = {
    "malware_detection": "Critical",
    "brute_force": "High",
    "suspicious_login": "Medium",
    "repeated_failed_login": "Medium",
}


def _is_failed_login(raw: str) -> bool:
    lower = raw.lower()
    return any(keyword in lower for keyword in FAILED_KEYWORDS)


def _is_malware(raw: str) -> bool:
    lower = raw.lower()
    return any(keyword in lower for keyword in MALWARE_KEYWORDS)


def _is_unknown_ip(ip: str) -> bool:
    try:
        parsed = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return not (parsed.is_private or parsed.is_loopback or parsed.is_multicast or parsed.is_reserved)


def _recent_alert_exists(db: Session, alert_type: str, ip: str, cutoff: datetime) -> bool:
    return (
        db.query(Alert)
        .filter(Alert.type == alert_type, Alert.ip == ip, Alert.timestamp >= cutoff)
        .order_by(desc(Alert.timestamp))
        .first()
        is not None
    )


def _create_alert(db: Session, alert_type: str, ip: str, timestamp: datetime, message: str) -> Alert:
    alert = Alert(
        type=alert_type,
        severity=SEVERITY_MAP[alert_type],
        ip=ip,
        timestamp=timestamp,
        message=message,
    )
    db.add(alert)
    return alert


def run_detection(db: Session, events: list[Event]) -> list[Alert]:
    if not events:
        return []

    new_alerts: list[Alert] = []
    created_in_batch: set[tuple[str, str]] = set()

    for event in events:
        ip = event.ip or "unknown"
        window_start = event.timestamp - timedelta(minutes=WINDOW_MINUTES)

        if _is_malware(event.raw_log):
            key = ("malware_detection", ip)
            if key not in created_in_batch and not _recent_alert_exists(db, "malware_detection", ip, window_start):
                new_alerts.append(
                    _create_alert(
                        db,
                        "malware_detection",
                        ip,
                        event.timestamp,
                        f"Malware signature detected in logs from {ip}.",
                    )
                )
                created_in_batch.add(key)

        if _is_failed_login(event.raw_log):
            failed_events = (
                db.query(Event)
                .filter(Event.ip == ip, Event.timestamp >= window_start)
                .order_by(Event.timestamp.asc())
                .all()
            )
            failed_count = sum(1 for row in failed_events if _is_failed_login(row.raw_log))

            if failed_count >= BRUTE_FORCE_THRESHOLD:
                key = ("brute_force", ip)
                if key not in created_in_batch and not _recent_alert_exists(db, "brute_force", ip, window_start):
                    new_alerts.append(
                        _create_alert(
                            db,
                            "brute_force",
                            ip,
                            event.timestamp,
                            f"Brute force pattern detected from {ip}: {failed_count} failed logins in 10 minutes.",
                        )
                    )
                    created_in_batch.add(key)
            elif failed_count >= REPEATED_FAILED_THRESHOLD:
                key = ("repeated_failed_login", ip)
                if key not in created_in_batch and not _recent_alert_exists(db, "repeated_failed_login", ip, window_start):
                    new_alerts.append(
                        _create_alert(
                            db,
                            "repeated_failed_login",
                            ip,
                            event.timestamp,
                            f"Repeated failed login attempts from {ip}: {failed_count} events in 10 minutes.",
                        )
                    )
                    created_in_batch.add(key)

        if _is_unknown_ip(ip):
            ip_event_count = (
                db.query(Event)
                .filter(Event.ip == ip, Event.timestamp >= window_start)
                .count()
            )
            if ip_event_count >= UNKNOWN_IP_SPIKE_THRESHOLD:
                key = ("suspicious_login", ip)
                if key not in created_in_batch and not _recent_alert_exists(db, "suspicious_login", ip, window_start):
                    new_alerts.append(
                        _create_alert(
                            db,
                            "suspicious_login",
                            ip,
                            event.timestamp,
                            f"Unknown IP spike from {ip}: {ip_event_count} events in 10 minutes.",
                        )
                    )
                    created_in_batch.add(key)

    if new_alerts:
        db.commit()
        for alert in new_alerts:
            db.refresh(alert)

    return new_alerts
