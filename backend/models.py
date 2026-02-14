from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Event(Base):
    __tablename__ = "siem_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    hostname: Mapped[str] = mapped_column(String(120), index=True, default="unknown")
    ip: Mapped[str] = mapped_column(String(64), index=True, default="unknown")
    raw_log: Mapped[str] = mapped_column(Text)


class Alert(Base):
    __tablename__ = "siem_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[str] = mapped_column(String(16), index=True)
    ip: Mapped[str] = mapped_column(String(64), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True, default=datetime.utcnow)
    message: Mapped[str] = mapped_column(Text)


class GeoRecord(Base):
    __tablename__ = "siem_geo_records"

    ip: Mapped[str] = mapped_column(String(64), primary_key=True)
    country: Mapped[str] = mapped_column(String(120), default="Unknown")
    city: Mapped[str] = mapped_column(String(120), default="Unknown")
    lat: Mapped[float] = mapped_column(Float, default=0.0)
    lon: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
