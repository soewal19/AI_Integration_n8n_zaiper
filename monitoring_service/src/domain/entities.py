from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Endpoint:
    name: str
    url: str
    method: str
    expected_status: int


@dataclass
class CheckResult:
    name: str
    url: str
    method: str
    expected_status: int
    actual_status: Optional[int]
    response_time_ms: Optional[int]
    status: str
    error: Optional[str] = None


@dataclass
class HealthReport:
    checked_at: datetime
    results: List[CheckResult] = field(default_factory=list)

    def to_json_dict(self) -> Dict[str, Any]:
        return {
            "checked_at": self.checked_at.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total": len(self.results),
                "failed": sum(1 for r in self.results if r.status == "failed"),
            },
            "results": [
                {
                    "name": r.name,
                    "url": r.url,
                    "method": r.method,
                    "expected_status": r.expected_status,
                    "actual_status": r.actual_status,
                    "response_time_ms": r.response_time_ms,
                    "status": r.status,
                    "error": r.error,
                }
                for r in self.results
            ],
        }

