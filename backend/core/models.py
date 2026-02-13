from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True, default=datetime.utcnow)
    source_type: Mapped[str] = mapped_column(String(20), index=True, default="syslog")
    device: Mapped[str] = mapped_column(String(120), index=True, default="unknown")
    ip: Mapped[str] = mapped_column(String(64), index=True, default="unknown")
    username: Mapped[str] = mapped_column(String(120), default="unknown")
    status: Mapped[str] = mapped_column(String(32), index=True, default="unknown")
    event_type: Mapped[str] = mapped_column(String(120), index=True, default="generic")
    raw: Mapped[str] = mapped_column(Text)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True, default=datetime.utcnow)
    ip: Mapped[str] = mapped_column(String(64), index=True, default="unknown")
    type: Mapped[str] = mapped_column(String(120), index=True)
    severity: Mapped[str] = mapped_column(String(20), index=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="New", index=True)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)


class RuleConfig(Base):
    __tablename__ = "rule_config"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[int] = mapped_column(Integer)


class SystemConfig(Base):
    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    live_monitoring: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BlockedIP(Base):
    __tablename__ = "blocked_ips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ip: Mapped[str] = mapped_column(String(64), index=True)
    reason: Mapped[str] = mapped_column(String(200), default="manual block")
    source_alert_id: Mapped[int | None] = mapped_column(ForeignKey("alerts.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
