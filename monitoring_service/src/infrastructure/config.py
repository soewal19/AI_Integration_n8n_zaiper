from __future__ import annotations
import json
import logging
import os
from pathlib import Path
from typing import List
from monitoring_service.src.domain.entities import Endpoint

logger = logging.getLogger(__name__)


def load_endpoints_config(config_path: Path) -> List[Endpoint]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    endpoints: List[Endpoint] = []
    for item in raw:
        endpoints.append(
            Endpoint(
                name=item["name"],
                url=item["url"],
                method=item.get("method", "GET").upper(),
                expected_status=int(item.get("expected_status", 200)),
            )
        )
    return endpoints


def get_slack_webhook_from_env() -> str | None:
    return os.environ.get("SLACK_WEBHOOK_URL") or None

