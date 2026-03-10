from __future__ import annotations
import json
import logging
from datetime import datetime
from typing import Optional
from urllib import request, error as urlerror

from monitoring_service.src.application.interfaces import Notifier
from monitoring_service.src.domain.entities import HealthReport
from monitoring_service.src.infrastructure.config import get_slack_webhook_from_env

logger = logging.getLogger(__name__)


def _post_json(url: str, payload: dict, timeout: float = 5.0) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url=url, data=data, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    with request.urlopen(req, timeout=timeout) as _:
        return


def _format_alert_text(report: HealthReport) -> str:
    checked_at = report.checked_at.strftime("%Y-%m-%d %H:%M:%S")
    failed = [r for r in report.results if r.status == "failed"]
    total = len(report.results)
    if failed:
        lines = [
            "🚨 Health Check Alert",
            f"Перевірка: {checked_at}",
            f"Ендпоінтів з помилкою: {len(failed)} із {total}",
        ]
        for r in failed:
            err = r.error or "Unknown error"
            rt = f"{r.response_time_ms}ms" if r.response_time_ms is not None else "n/a"
            lines.extend(
                [
                    f"❌ {r.name}",
                    f"URL: `{r.url}`",
                    f"Помилка: {err}" + (f" (status={r.actual_status})" if r.actual_status is not None else ""),
                    f"Час відповіді: {rt}",
                ]
            )
        return "\n".join(lines)
    else:
        return f"✅ Health Check OK — всі {total} ендпоінти доступні ({checked_at})"


class SlackOrConsoleNotifier(Notifier):
    def __init__(self, webhook_url: Optional[str]) -> None:
        self.webhook_url = webhook_url

    def notify(self, report: HealthReport, quiet: bool = False) -> None:
        text = _format_alert_text(report)
        def _safe_print(msg: str) -> None:
            import sys
            try:
                print(msg)
            except UnicodeEncodeError:
                enc = sys.stdout.encoding or "utf-8"
                print(msg.encode(enc, errors="replace").decode(enc, errors="replace"))
        if quiet:
            logger.info("Quiet mode enabled; skipping Slack send.")
            _safe_print(text)
            return
        if not self.webhook_url:
            logger.warning("SLACK_WEBHOOK_URL not set; printing message instead.")
            _safe_print(text)
            return
        try:
            _post_json(self.webhook_url, {"text": text})
            logger.info("Alert sent to Slack")
        except urlerror.URLError as e:
            logger.error("Failed to send Slack alert: %s", e)
            _safe_print(text)
        except Exception as e:
            logger.exception("Unexpected error sending Slack alert: %s", e)
            _safe_print(text)
