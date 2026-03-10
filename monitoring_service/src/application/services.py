from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Iterable

from monitoring_service.src.domain.entities import Endpoint, CheckResult, HealthReport
from monitoring_service.src.application.interfaces import HTTPChecker, Notifier, ResultsRepository


logger = logging.getLogger(__name__)


class MonitoringService:
    def __init__(
        self,
        checker: HTTPChecker,
        notifier: Notifier,
        repo: ResultsRepository | None,
        report_path: Path,
    ) -> None:
        self.checker = checker
        self.notifier = notifier
        self.repo = repo
        self.report_path = report_path

    def run_check(self, endpoints: Iterable[Endpoint], quiet: bool = False) -> HealthReport:
        checked_at = datetime.now()
        logger.info("Starting health check for %d endpoints", len(list(endpoints)))
        results: List[CheckResult] = self.checker.check_many(endpoints)
        report = HealthReport(checked_at=checked_at, results=results)
        self._write_report(report)
        if self.repo:
            try:
                self.repo.save_results(checked_at, results)
            except Exception as e:
                logger.exception("Failed to save results to repository: %s", e)
        self.notifier.notify(report, quiet=quiet)
        return report

    def _write_report(self, report: HealthReport) -> None:
        data = report.to_json_dict()
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        with self.report_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Health report written to %s", self.report_path)

