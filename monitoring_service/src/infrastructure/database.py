from __future__ import annotations
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List

from monitoring_service.src.domain.entities import CheckResult
from monitoring_service.src.application.interfaces import ResultsRepository

logger = logging.getLogger(__name__)


class SQLiteResultsRepository(ResultsRepository):
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    check_time TEXT NOT NULL,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    method TEXT NOT NULL,
                    expected_status INTEGER NOT NULL,
                    actual_status INTEGER,
                    response_time_ms INTEGER,
                    status TEXT NOT NULL,
                    error TEXT
                )
                """
            )
            conn.commit()

    def save_results(self, checked_at: datetime, results: List[CheckResult]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            rows = [
                (
                    checked_at.strftime("%Y-%m-%d %H:%M:%S"),
                    r.name,
                    r.url,
                    r.method,
                    r.expected_status,
                    r.actual_status,
                    r.response_time_ms,
                    r.status,
                    r.error,
                )
                for r in results
            ]
            conn.executemany(
                """
                INSERT INTO results (
                    check_time, name, url, method, expected_status, actual_status, response_time_ms, status, error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.commit()
            logger.info("Saved %d result rows to %s", len(rows), self.db_path)

