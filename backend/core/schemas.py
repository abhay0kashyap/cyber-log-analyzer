from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AlertOut(BaseModel):
    id: int
    timestamp: datetime
    ip: str
    type: str
    severity: str
    description: str
    status: str
    blocked: bool
    risk_score: int = 0
    high_risk: bool = False


class StatsOut(BaseModel):
    total_events: int
    windows_events: int
    syslog_events: int
    all_devices: int


class ThresholdSettings(BaseModel):
    brute_force_count: int = Field(10, ge=1, le=10000)
    repeated_failed_threshold: int = Field(5, ge=1, le=10000)
    unknown_ip_spike_threshold: int = Field(15, ge=1, le=10000)


class SettingsOut(ThresholdSettings):
    live_monitoring: bool = True


class AlertStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(New|Investigating|Resolved)$")


class AlertListResponse(BaseModel):
    items: list[AlertOut]
    total: int
    page: int
    page_size: int
    total_pages: int
    severity_counts: dict[str, int]


class LiveEventPayload(BaseModel):
    timestamp: str
    event_count: int
    source_type: str
    ip: str
    status: str


class LiveAlertPayload(BaseModel):
    id: int
    timestamp: str
    ip: str
    type: str
    severity: str
    description: str
    status: str
