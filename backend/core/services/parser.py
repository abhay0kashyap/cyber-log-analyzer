from __future__ import annotations

import csv
import io
import json
import re
from datetime import datetime

WINDOWS_AUTH_RE = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}).*?(?P<device>[\w\-.]+).*?(?P<event>failed login|success login|logon failure|login failed|logon success).*?(?P<ip>\d+\.\d+\.\d+\.\d+)",
    re.IGNORECASE,
)
SYSLOG_RE = re.compile(
    r"^(?P<month>\w{3})\s+(?P<day>\d{1,2})\s+(?P<clock>\d{2}:\d{2}:\d{2})\s+(?P<device>[\w\-.]+)\s+.*?(?:from|SRC=)\s*(?P<ip>\d+\.\d+\.\d+\.\d+)?",
    re.IGNORECASE,
)
FAILED_RE = re.compile(r"failed|failure|invalid|denied", re.IGNORECASE)
USER_RE = re.compile(r"(?:user|for)\s+([\w\-.]+)", re.IGNORECASE)

MONTH_MAP = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def _parse_timestamp(raw: str | None) -> datetime:
    if not raw:
        return datetime.utcnow()
    for candidate in (raw, raw.replace("Z", "+00:00"), raw.replace(" ", "T")):
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            continue
    return datetime.utcnow()


def _parse_syslog_time(month: str, day: str, clock: str) -> datetime:
    now = datetime.utcnow()
    month_num = MONTH_MAP.get(month.lower(), now.month)
    return datetime.strptime(f"{now.year}-{month_num:02d}-{int(day):02d} {clock}", "%Y-%m-%d %H:%M:%S")


def _build_event(raw: str, **kwargs) -> dict:
    return {
        "timestamp": kwargs.get("timestamp", datetime.utcnow()),
        "source_type": kwargs.get("source_type", "syslog").lower(),
        "device": kwargs.get("device", "unknown"),
        "ip": kwargs.get("ip", "unknown"),
        "username": kwargs.get("username", "unknown"),
        "status": kwargs.get("status", "unknown").lower(),
        "event_type": kwargs.get("event_type", "generic"),
        "raw": raw.strip(),
    }


def _parse_json_line(raw: str) -> dict | None:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return _build_event(
        raw,
        timestamp=_parse_timestamp(payload.get("timestamp")),
        source_type=str(payload.get("source_type", "syslog")),
        device=str(payload.get("device", "unknown")),
        ip=str(payload.get("ip", "unknown")),
        username=str(payload.get("username", "unknown")),
        status=str(payload.get("status", "unknown")),
        event_type=str(payload.get("event_type", "system")),
    )


def parse_line(line: str) -> dict | None:
    raw = line.strip()
    if not raw:
        return None

    json_row = _parse_json_line(raw)
    if json_row:
        return json_row

    windows = WINDOWS_AUTH_RE.search(raw)
    if windows:
        event_lower = windows.group("event").lower()
        status = "failed" if "fail" in event_lower else "success"
        user_match = USER_RE.search(raw)
        username = user_match.group(1) if user_match else "unknown"
        return _build_event(
            raw,
            timestamp=_parse_timestamp(windows.group("timestamp")),
            source_type="windows",
            device=windows.group("device"),
            ip=windows.group("ip"),
            username=username,
            status=status,
            event_type="authentication",
        )

    syslog = SYSLOG_RE.search(raw)
    if syslog:
        user_match = USER_RE.search(raw)
        username = user_match.group(1) if user_match else "unknown"
        status = "failed" if FAILED_RE.search(raw) else "success"
        return _build_event(
            raw,
            timestamp=_parse_syslog_time(syslog.group("month"), syslog.group("day"), syslog.group("clock")),
            source_type="syslog",
            device=syslog.group("device"),
            ip=syslog.group("ip") or "unknown",
            username=username,
            status=status,
            event_type="authentication" if "ssh" in raw.lower() else "system",
        )

    return _build_event(raw, source_type="syslog", event_type="unparsed")


def _parse_csv(content: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(content))
    records: list[dict] = []
    for row in reader:
        raw = json.dumps(row)
        records.append(
            _build_event(
                raw,
                timestamp=_parse_timestamp(row.get("timestamp")),
                source_type=(row.get("source_type") or row.get("type") or "syslog"),
                device=row.get("device") or row.get("host") or "unknown",
                ip=row.get("ip") or row.get("source_ip") or "unknown",
                username=row.get("username") or row.get("user") or "unknown",
                status=row.get("status") or "unknown",
                event_type=row.get("event_type") or row.get("event") or "system",
            )
        )
    return records


def parse_log_content(content: str, filename: str = "") -> list[dict]:
    if not content.strip():
        return []

    lower_name = filename.lower()
    if lower_name.endswith(".csv"):
        return _parse_csv(content)

    parsed: list[dict] = []
    for line in content.splitlines():
        row = parse_line(line)
        if row:
            parsed.append(row)
    return parsed
