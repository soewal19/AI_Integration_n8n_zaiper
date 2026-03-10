from __future__ import annotations
import json
import logging
import os
from typing import Optional
from urllib import request, parse, error as urlerror

from monitoring_service.src.application.interfaces import Notifier
from monitoring_service.src.domain.entities import HealthReport

logger = logging.getLogger(__name__)


def _format_text(report: HealthReport) -> str:
    checked_at = report.checked_at.strftime("%Y-%m-%d %H:%M:%S")
    failed = [r for r in report.results if r.status == "failed"]
    total = len(report.results)
    if failed:
        lines = [f"🚨 Health Check Alert\nПроверка: {checked_at}\nС ошибкой: {len(failed)} из {total}"]
        for r in failed:
            rt = f"{r.response_time_ms}ms" if r.response_time_ms is not None else "n/a"
            lines.append(f"❌ {r.name}\nURL: {r.url}\nОшибка: {r.error}\nRT: {rt}")
        return "\n\n".join(lines)
    else:
        return f"✅ Health Check OK — все {total} эндпоинта доступны ({checked_at})"


class TelegramNotifier(Notifier):
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None) -> None:
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")

    def notify(self, report: HealthReport, quiet: bool = False) -> None:
        if quiet:
            return
        if not self.bot_token or not self.chat_id:
            logger.info("Telegram config is missing; skipping Telegram notify")
            return
        text = _format_text(report)
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text}
        data = parse.urlencode(payload).encode("utf-8")
        req = request.Request(url=url, data=data, method="POST")
        try:
            with request.urlopen(req, timeout=5) as _:
                logger.info("Alert sent to Telegram")
        except urlerror.URLError as e:
            logger.error("Failed to send Telegram alert: %s", e)
        except Exception as e:
            logger.exception("Unexpected error sending Telegram alert: %s", e)

