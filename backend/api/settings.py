from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import SystemConfig
from core.schemas import SettingsOut, ThresholdSettings
from core.services.detector import get_thresholds, save_thresholds

router = APIRouter(prefix="/settings", tags=["settings"])


def _get_monitor_row(db: Session) -> SystemConfig:
    row = db.get(SystemConfig, 1)
    if row is None:
        row = SystemConfig(id=1, live_monitoring=True)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


@router.get("", response_model=SettingsOut)
async def get_settings(db: Session = Depends(get_db)):
    thresholds = get_thresholds(db)
    monitor = _get_monitor_row(db)
    return {
        "brute_force_count": thresholds["brute_force_count"],
        "repeated_failed_threshold": thresholds["repeated_failed_threshold"],
        "unknown_ip_spike_threshold": thresholds["unknown_ip_spike_threshold"],
        "live_monitoring": monitor.live_monitoring,
    }


@router.post("", response_model=SettingsOut)
async def save_settings(payload: SettingsOut, db: Session = Depends(get_db)):
    thresholds = save_thresholds(
        db,
        {
            "brute_force_count": payload.brute_force_count,
            "repeated_failed_threshold": payload.repeated_failed_threshold,
            "unknown_ip_spike_threshold": payload.unknown_ip_spike_threshold,
        },
    )
    monitor = _get_monitor_row(db)
    monitor.live_monitoring = payload.live_monitoring
    monitor.updated_at = datetime.utcnow()
    db.commit()

    return {
        "brute_force_count": thresholds["brute_force_count"],
        "repeated_failed_threshold": thresholds["repeated_failed_threshold"],
        "unknown_ip_spike_threshold": thresholds["unknown_ip_spike_threshold"],
        "live_monitoring": monitor.live_monitoring,
    }
