from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BASE_DIR / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_DIR / 'cyber_log_analyzer.db'}")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def _sqlite_column_exists(db_engine: Engine, table: str, column: str) -> bool:
    with db_engine.begin() as conn:
        rows = conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == column for r in rows)


def _sqlite_table_columns(db_engine: Engine, table: str) -> set[str]:
    with db_engine.begin() as conn:
        rows = conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
    return {r[1] for r in rows}


def _apply_sqlite_migrations(db_engine: Engine) -> None:
    if not str(db_engine.url).startswith("sqlite"):
        return

    migrations = [
        ("alerts", "description", "ALTER TABLE alerts ADD COLUMN description TEXT"),
        ("alerts", "status", "ALTER TABLE alerts ADD COLUMN status VARCHAR(32) DEFAULT 'New'"),
        ("alerts", "blocked", "ALTER TABLE alerts ADD COLUMN blocked BOOLEAN DEFAULT 0"),
    ]

    for table, column, sql in migrations:
        if _sqlite_column_exists(db_engine, table, column):
            continue
        with db_engine.begin() as conn:
            conn.exec_driver_sql(sql)

    alert_columns = _sqlite_table_columns(db_engine, "alerts")
    if "description" in alert_columns and "details" in alert_columns:
        with db_engine.begin() as conn:
            conn.exec_driver_sql(
                "UPDATE alerts SET description = details "
                "WHERE (description IS NULL OR description = '') AND details IS NOT NULL"
            )


def init_db() -> None:
    # Import models here so metadata is fully registered before create_all.
    from core import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _apply_sqlite_migrations(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
