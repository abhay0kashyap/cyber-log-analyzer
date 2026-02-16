from __future__ import annotations

import ipaddress
import json
from datetime import datetime
from urllib.error import URLError
from urllib.request import urlopen

from sqlalchemy.orm import Session

from backend.models import GeoRecord


def _is_public_ip(ip: str) -> bool:
    try:
        parsed = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return not (parsed.is_private or parsed.is_loopback or parsed.is_multicast or parsed.is_reserved)


def _lookup_ip_geo(ip: str) -> dict:
    if not _is_public_ip(ip):
        return {"country": "Private", "city": "Private", "lat": 0.0, "lon": 0.0}

    url = f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon"
    try:
        with urlopen(url, timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, OSError, json.JSONDecodeError):
        return {"country": "Unknown", "city": "Unknown", "lat": 0.0, "lon": 0.0}

    if payload.get("status") != "success":
        return {"country": "Unknown", "city": "Unknown", "lat": 0.0, "lon": 0.0}

    return {
        "country": str(payload.get("country") or "Unknown"),
        "city": str(payload.get("city") or "Unknown"),
        "lat": float(payload.get("lat") or 0.0),
        "lon": float(payload.get("lon") or 0.0),
    }


def get_or_create_geo(db: Session, ip: str) -> GeoRecord:
    record = db.get(GeoRecord, ip)
    if record is not None:
        return record

    geo = _lookup_ip_geo(ip)
    record = GeoRecord(
        ip=ip,
        country=geo["country"],
        city=geo["city"],
        lat=geo["lat"],
        lon=geo["lon"],
        updated_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def build_geo_feed(db: Session, top_ips: list[dict]) -> list[dict]:
    feed: list[dict] = []
    for row in top_ips:
        ip = row["ip"]
        count = int(row["count"])
        record = get_or_create_geo(db, ip)
        feed.append(
            {
                "ip": ip,
                "count": count,
                "country": record.country,
                "city": record.city,
                "lat": record.lat,
                "lon": record.lon,
            }
        )
    return feed

