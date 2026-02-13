from __future__ import annotations

from datetime import datetime, timedelta
import random

from core.database import SessionLocal, init_db
from core.models import Event
from core.services.correlation import run_correlation_engine
from core.services.detector import detect_anomalies

IPS = [
    "10.0.0.12",
    "10.0.1.24",
    "172.16.4.9",
    "185.220.101.4",
    "91.214.124.77",
    "45.95.147.12",
]
DEVICES = ["vpn-gateway", "dc-01", "mail-01", "edge-fw", "linux-app-07"]


def _raw_payload(ip: str) -> str:
    roll = random.random()
    if roll < 0.08:
        return f"powershell -enc suspicious payload malware from {ip}"
    if roll < 0.35:
        return f"failed password for root from {ip}"
    return f"accepted password for user from {ip}"


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        events: list[Event] = []
        for _ in range(320):
            ip = random.choice(IPS)
            ts = now - timedelta(minutes=random.randint(0, 180))
            raw = _raw_payload(ip)
            status = "failed" if "failed" in raw else "success"
            event = Event(
                timestamp=ts,
                source_type="windows" if random.random() < 0.4 else "syslog",
                device=random.choice(DEVICES),
                ip=ip,
                username=random.choice(["alice", "bob", "root", "admin", "svc-auth"]),
                status=status,
                event_type="authentication",
                raw=raw,
            )
            db.add(event)
            events.append(event)

        db.commit()
        for item in events:
            db.refresh(item)

        detect_anomalies(db, events)
        correlated = run_correlation_engine(db)
        print(f"Seeded {len(events)} events. Correlated alerts generated: {len(correlated)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
