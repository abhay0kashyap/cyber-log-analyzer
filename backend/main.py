from __future__ import annotations

import re
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Literal, TypedDict

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from api.alerts import router as alerts_router
from api.logs import router as logs_router
from api.reports import router as reports_router
from api.settings import router as settings_router
from api.stats import router as stats_router
from core.database import init_db
from ws import ws_manager

SeverityLevel = Literal["Low", "Medium", "High", "Critical"]


class ParsedLogEntry(TypedDict):
    timestamp: datetime
    ip: str
    message: str
    raw: str


class UploadAlert(TypedDict):
    id: int
    timestamp: str
    ip: str
    type: str
    severity: SeverityLevel
    description: str


class TopIpEntry(TypedDict):
    ip: str
    count: int


# In-memory runtime state used by the /upload endpoint.
in_memory_events: list[ParsedLogEntry] = []
in_memory_alerts: list[UploadAlert] = []
failed_attempts_by_ip: dict[str, list[datetime]] = {}
ip_event_counts: dict[str, int] = {}
severity_counters: dict[str, int] = {"low": 0, "medium": 0, "high": 0, "critical": 0}
last_bruteforce_alert_end_by_ip: dict[str, datetime] = {}
suspicious_login_alerted_ips: set[str] = set()
next_alert_id = 1

FAILED_PASSWORD_KEYWORD = "failed password"
MALWARE_KEYWORD = "malware"
BRUTE_FORCE_THRESHOLD = 5
SUSPICIOUS_LOGIN_THRESHOLD = 50
BRUTE_FORCE_WINDOW = timedelta(minutes=10)

SYSLOG_PATTERN = re.compile(
    r"^(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s\d{2}:\d{2}:\d{2})\s+\S+\s+[^:]+:\s*(?P<message>.*)$"
)
TIMESTAMP_PREFIX_PATTERN = re.compile(r"^(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s\d{2}:\d{2}:\d{2})")
IPV4_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Cyber Log Analyzer API", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stats_router)
app.include_router(alerts_router)
app.include_router(logs_router)
app.include_router(reports_router)
app.include_router(settings_router)


@app.get("/")
async def root():
    return {"message": "Cyber Log Analyzer API running 🚀"}


@app.get("/health")
async def health():
    return {"status": "ok"}


def parse_log_line(line: str, now: datetime | None = None) -> ParsedLogEntry | None:
    """
    Parse one uploaded line and extract timestamp, source IP, and message.
    """
    raw = line.strip()
    if not raw:
        return None

    now_dt = now or datetime.now()
    timestamp = now_dt

    timestamp_match = TIMESTAMP_PREFIX_PATTERN.match(raw)
    if timestamp_match:
        try:
            timestamp = datetime.strptime(timestamp_match.group("ts"), "%b %d %H:%M:%S").replace(year=now_dt.year)
            # Handle year boundary in syslog-like records.
            if timestamp - now_dt > timedelta(days=1):
                timestamp = timestamp.replace(year=now_dt.year - 1)
        except ValueError:
            timestamp = now_dt

    message_match = SYSLOG_PATTERN.match(raw)
    message = message_match.group("message") if message_match else raw

    ip_match = IPV4_PATTERN.search(raw)
    if ip_match is None:
        return None

    return {
        "timestamp": timestamp,
        "ip": ip_match.group(0),
        "message": message,
        "raw": raw,
    }


def is_failed_password(message: str) -> bool:
    return FAILED_PASSWORD_KEYWORD in message.lower()


def track_failed_login_attempts(ip: str, timestamp: datetime) -> list[datetime]:
    """
    Track failed-password events for an IP and keep only the last 10 minutes.
    """
    attempts = failed_attempts_by_ip.setdefault(ip, [])
    attempts.append(timestamp)
    cutoff = timestamp - BRUTE_FORCE_WINDOW
    active_attempts = [ts for ts in attempts if ts >= cutoff]
    failed_attempts_by_ip[ip] = active_attempts
    return active_attempts


def create_alert(ip: str, alert_type: str, severity: SeverityLevel, description: str, timestamp: datetime) -> UploadAlert:
    """
    Create and persist an in-memory alert while updating severity counters.
    """
    global next_alert_id

    alert: UploadAlert = {
        "id": next_alert_id,
        "timestamp": timestamp.isoformat(),
        "ip": ip,
        "type": alert_type,
        "severity": severity,
        "description": description,
    }
    next_alert_id += 1

    in_memory_alerts.append(alert)
    severity_counters[severity.lower()] += 1
    return alert


def evaluate_bruteforce_rule(ip: str, attempts: list[datetime]) -> UploadAlert | None:
    """
    Rule: 5+ 'Failed password' events from same IP in 10 minutes -> brute_force (High).
    """
    ordered_attempts = sorted(attempts)
    if len(ordered_attempts) < BRUTE_FORCE_THRESHOLD:
        return None

    last_alert_end = last_bruteforce_alert_end_by_ip.get(ip)
    if last_alert_end and ordered_attempts[-1] <= last_alert_end:
        return None

    return create_alert(
        ip=ip,
        alert_type="brute_force",
        severity="High",
        description=(
            f"Brute force detected from {ip}: "
            f"{len(ordered_attempts)} failed password attempts in 10 minutes."
        ),
        timestamp=ordered_attempts[-1],
    )


def evaluate_malware_rule(entry: ParsedLogEntry) -> UploadAlert | None:
    """
    Rule: 'malware' keyword in message -> malware_detection (Critical).
    """
    if MALWARE_KEYWORD not in entry["message"].lower():
        return None

    return create_alert(
        ip=entry["ip"],
        alert_type="malware_detection",
        severity="Critical",
        description=f"Malware keyword detected in event from {entry['ip']}.",
        timestamp=entry["timestamp"],
    )


def evaluate_suspicious_login_rule(ip: str, timestamp: datetime) -> UploadAlert | None:
    """
    Rule: 50+ events from same IP -> suspicious_login (Medium).
    """
    count = ip_event_counts.get(ip, 0)
    if count < SUSPICIOUS_LOGIN_THRESHOLD or ip in suspicious_login_alerted_ips:
        return None

    suspicious_login_alerted_ips.add(ip)
    return create_alert(
        ip=ip,
        alert_type="suspicious_login",
        severity="Medium",
        description=f"Suspicious activity from {ip}: {count} events observed.",
        timestamp=timestamp,
    )


def build_top_ips(limit: int = 10) -> list[TopIpEntry]:
    ranked = sorted(ip_event_counts.items(), key=lambda item: item[1], reverse=True)
    return [{"ip": ip, "count": count} for ip, count in ranked[:limit]]


@app.post("/upload")
async def upload_soc_logs(file: UploadFile = File(...)):
    """
    Upload SOC logs, parse line by line, and evaluate attack detection rules.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    content = (await file.read()).decode("utf-8", errors="ignore")
    new_alerts: list[UploadAlert] = []
    brute_force_alerted_ips_in_upload: set[str] = set()

    for line in content.splitlines():
        parsed = parse_log_line(line)
        if parsed is None:
            continue

        in_memory_events.append(parsed)
        ip = parsed["ip"]
        ip_event_counts[ip] = ip_event_counts.get(ip, 0) + 1

        if is_failed_password(parsed["message"]):
            attempts = track_failed_login_attempts(ip, parsed["timestamp"])
            brute_force_alert = evaluate_bruteforce_rule(ip, attempts)
            if brute_force_alert and ip not in brute_force_alerted_ips_in_upload:
                new_alerts.append(brute_force_alert)
                brute_force_alerted_ips_in_upload.add(ip)
                last_bruteforce_alert_end_by_ip[ip] = datetime.fromisoformat(brute_force_alert["timestamp"])

        malware_alert = evaluate_malware_rule(parsed)
        if malware_alert:
            new_alerts.append(malware_alert)

        suspicious_login_alert = evaluate_suspicious_login_rule(ip, parsed["timestamp"])
        if suspicious_login_alert:
            new_alerts.append(suspicious_login_alert)

    return {
        "total_events": len(in_memory_events),
        "severity": severity_counters,
        "top_ips": build_top_ips(),
        "alerts": list(reversed(in_memory_alerts[-100:])),
        "new_alerts": new_alerts,
    }


@app.websocket("/ws/live")
async def ws_live(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
