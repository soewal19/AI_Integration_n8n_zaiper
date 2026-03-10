from typing import Optional, Literal, Dict, Any, List
from datetime import datetime
try:
    from pydantic import BaseModel, Field
except Exception:
    BaseModel = object  # fallback to avoid import error
    Field = lambda default=None, **_: default


class EndpointModel(BaseModel):
    name: str
    url: str
    method: Literal["GET", "POST", "PUT", "DELETE"] = "GET"
    expected_status: int = 200
    headers: Optional[Dict[str, Any]] = None


class HealthCheckResultModel(BaseModel):
    endpoint_name: str
    url: str
    status: Literal["ok", "failed"]
    response_time_ms: float
    expected_status: int
    actual_status: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    @property
    def is_failed(self) -> bool:
        return self.status == "failed"

