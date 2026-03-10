from __future__ import annotations
from typing import Protocol, Iterable, List
from datetime import datetime
from monitoring_service.src.domain.entities import Endpoint, CheckResult, HealthReport


class HTTPChecker(Protocol):
    def check_many(self, endpoints: Iterable[Endpoint]) -> List[CheckResult]:
        ...


class Notifier(Protocol):
    def notify(self, report: HealthReport, quiet: bool = False) -> None:
        ...


class ResultsRepository(Protocol):
    def save_results(self, checked_at: datetime, results: List[CheckResult]) -> None:
        ...

