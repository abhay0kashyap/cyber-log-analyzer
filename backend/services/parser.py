from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from typing import TypedDict


class ParsedEvent(TypedDict):
    timestamp: datetime
    source: str
    hostname: str
    ip: str
    raw_log: str


IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
SYSLOG_RE = re.compile(
    r"^(?P<month>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\s+(?P<clock>\d{2}:\d{2}:\d{2})\s+(?P<hostname>[\w\-.]+)"
)
ISO_TS_RE = re.compile(r"(?P<ts>\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})")
MONTH_MAP = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def _parse_timestamp(line: str) -> datetime:
    iso_match = ISO_TS_RE.search(line)
    if iso_match:
        raw = iso_match.group("ts").replace(" ", "T")
        try:
            parsed = datetime.fromisoformat(raw)
            if parsed.tzinfo is not None:
                return parsed.astimezone(UTC).replace(tzinfo=None)
            # Treat naive ISO timestamps as UTC.
            return parsed
        except ValueError:
            pass

    syslog_match = SYSLOG_RE.match(line)
    if syslog_match:
        now = datetime.now(UTC)
        month = MONTH_MAP.get(syslog_match.group("month"), now.month)
        day = int(syslog_match.group("day"))
        clock = syslog_match.group("clock")
        parsed = datetime.strptime(f"{now.year}-{month:02d}-{day:02d} {clock}", "%Y-%m-%d %H:%M:%S")
        parsed = parsed.replace(tzinfo=UTC)
        # Only roll back a year when the parsed timestamp is implausibly far in the future.
        if parsed - now > timedelta(days=30):
            parsed = parsed.replace(year=parsed.year - 1)
        return parsed.replace(tzinfo=None)

    return datetime.utcnow()


def _detect_source(line: str) -> str:
    lower = line.lower()
    windows_markers = ("eventid", "winlogon", "security-auditing", "an account failed to log on")
    if any(marker in lower for marker in windows_markers):
        return "windows"
    return "syslog"


def _detect_hostname(line: str) -> str:
    match = SYSLOG_RE.match(line)
    if match:
        return match.group("hostname")

    parts = line.split()
    if len(parts) >= 2 and ISO_TS_RE.match(parts[0]):
        return parts[1]
    return "unknown"


def parse_log_line(line: str) -> ParsedEvent | None:
    raw = line.strip()
    if not raw:
        return None

    ip_match = IP_RE.search(raw)
    ip = ip_match.group(0) if ip_match else "unknown"

    return {
        "timestamp": _parse_timestamp(raw),
        "source": _detect_source(raw),
        "hostname": _detect_hostname(raw),
        "ip": ip,
        "raw_log": raw,
    }


def parse_log_content(content: str) -> list[ParsedEvent]:
    parsed: list[ParsedEvent] = []
    for line in content.splitlines():
        event = parse_log_line(line)
        if event is not None:
            parsed.append(event)
    return parsed
