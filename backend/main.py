from __future__ import annotations

import re
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
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


class ParsedLogEntry(TypedDict):
    timestamp: datetime
    ip: str
    message: str
    raw: str


class BruteForceAlert(TypedDict):
    type: Literal["brute_force"]
    ip: str
    start: str
    end: str
    count: int


# In-memory stores for /upload endpoint.
in_memory_events: list[ParsedLogEntry] = []
in_memory_alerts: list[BruteForceAlert] = []
failed_attempts_by_ip: dict[str, list[datetime]] = {}
last_bruteforce_alert_end_by_ip: dict[str, datetime] = {}

FAILED_LOGIN_KEYWORDS = ("failed password", "failed login", "authentication failure")
BRUTE_FORCE_THRESHOLD = 5
BRUTE_FORCE_WINDOW = timedelta(minutes=10)

SYSLOG_PATTERN = re.compile(
    r"^(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s\d{2}:\d{2}:\d{2})\s+\S+\s+[^:]+:\s*(?P<message>.*)$"
)
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
    Parse one syslog-like line into a structured record.
    Expected example: 'Feb 15 03:10:01 server sshd: Failed password ... from 10.10.10.10'
    """
    raw = line.strip()
    if not raw:
        return None

    match = SYSLOG_PATTERN.match(raw)
    if not match:
        return None

    now_dt = now or datetime.now()
    try:
        timestamp = datetime.strptime(match.group("ts"), "%b %d %H:%M:%S").replace(year=now_dt.year)
    except ValueError:
        return None
    # If logs are from late Dec and we're in early Jan, shift to previous year.
    if timestamp - now_dt > timedelta(days=1):
        timestamp = timestamp.replace(year=now_dt.year - 1)

    message = match.group("message")
    ip_match = IPV4_PATTERN.search(message)
    if not ip_match:
        return None

    return {
        "timestamp": timestamp,
        "ip": ip_match.group(0),
        "message": message,
        "raw": raw,
    }


def is_failed_login(message: str) -> bool:
    lower = message.lower()
    return any(keyword in lower for keyword in FAILED_LOGIN_KEYWORDS)


def track_failed_attempt(ip: str, timestamp: datetime) -> list[datetime]:
    """
    Track failed logins for one IP and retain only events inside the 10-minute window.
    """
    attempts = failed_attempts_by_ip.setdefault(ip, [])
    attempts.append(timestamp)
    cutoff = timestamp - BRUTE_FORCE_WINDOW
    failed_attempts_by_ip[ip] = [ts for ts in attempts if ts >= cutoff]
    return failed_attempts_by_ip[ip]


def evaluate_bruteforce_rule(ip: str, attempts: list[datetime]) -> BruteForceAlert | None:
    """
    If an IP has >= threshold failed attempts in the active window, emit a brute force alert.
    """
    sorted_attempts = sorted(attempts)
    if len(sorted_attempts) < BRUTE_FORCE_THRESHOLD:
        return None

    last_alert_end = last_bruteforce_alert_end_by_ip.get(ip)
    if last_alert_end is not None and sorted_attempts[-1] <= last_alert_end:
        return None

    return {
        "type": "brute_force",
        "ip": ip,
        "start": sorted_attempts[0].isoformat(),
        "end": sorted_attempts[-1].isoformat(),
        "count": len(sorted_attempts),
    }


@app.post("/upload")
async def upload_soc_logs(file: UploadFile = File(...)):
    """
    Upload SOC logs, parse line-by-line, and detect brute force attacks.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    content = (await file.read()).decode("utf-8", errors="ignore")
    new_alerts: list[BruteForceAlert] = []
    alerted_ips_in_upload: set[str] = set()

    for line in content.splitlines():
        parsed = parse_log_line(line)
        if parsed is None:
            continue

        in_memory_events.append(parsed)

        if not is_failed_login(parsed["message"]):
            continue

        ip = parsed["ip"]
        attempts = track_failed_attempt(ip, parsed["timestamp"])
        alert = evaluate_bruteforce_rule(ip, attempts)
        if alert and ip not in alerted_ips_in_upload:
            in_memory_alerts.append(alert)
            new_alerts.append(alert)
            alerted_ips_in_upload.add(ip)
            last_bruteforce_alert_end_by_ip[ip] = datetime.fromisoformat(alert["end"])

    return {
        "filename": file.filename,
        "total_events": len(in_memory_events),
        "alert_count": len(in_memory_alerts),
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
