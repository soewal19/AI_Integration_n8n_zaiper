from __future__ import annotations
import argparse
import logging
import os
import sys
import time
from pathlib import Path

from monitoring_service.src.application.services import MonitoringService
from monitoring_service.src.infrastructure.config import load_endpoints_config, get_slack_webhook_from_env
from monitoring_service.src.infrastructure.http_client import ParallelHTTPChecker
from monitoring_service.src.infrastructure.notifiers import SlackOrConsoleNotifier
from monitoring_service.src.infrastructure.database import SQLiteResultsRepository


LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logger = logging.getLogger("monitor")


def _load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    try:
        with env_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ.setdefault(key, value)
    except Exception:
        logger.exception("Failed to load env file: %s", env_path)


def _setup_logging_from_env() -> None:
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format=LOG_FORMAT)


def build_service(project_root: Path, report_filename: str = "health_report.json") -> tuple[MonitoringService, list]:
    # Allow overriding via env
    config_path_env = os.environ.get("CONFIG_PATH")
    config_path = Path(config_path_env) if config_path_env else (project_root / "config" / "endpoints.json")
    endpoints = load_endpoints_config(config_path)

    checker = ParallelHTTPChecker(timeout_seconds=5.0, max_workers=8)
    webhook = get_slack_webhook_from_env()
    notifier = SlackOrConsoleNotifier(webhook_url=webhook)
    db_path_env = os.environ.get("DB_PATH")
    db_path = Path(db_path_env) if db_path_env else (project_root / "monitoring_service" / "health_history.db")
    repo = SQLiteResultsRepository(db_path=db_path)
    report_path = project_root / report_filename
    service = MonitoringService(checker=checker, notifier=notifier, repo=repo, report_path=report_path)
    return service, endpoints


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="API Health Check Monitor")
    parser.add_argument("--check", action="store_true", help="Run a single health check")
    parser.add_argument("--watch", action="store_true", help="Run checks in a loop")
    parser.add_argument("--quiet", action="store_true", help="Do not send Slack alerts; print to console")
    parser.add_argument("--interval", type=int, default=60, help="Interval seconds for --watch (default: 60)")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[3]
    # Load env file if present and configure logging
    _load_env_file(root / "config" / "settings.env")
    _setup_logging_from_env()
    service, endpoints = build_service(root)

    if args.check:
        report = service.run_check(endpoints, quiet=args.quiet)
        failed = sum(1 for r in report.results if r.status == "failed")
        return 1 if failed else 0
    elif args.watch:
        logger.info("Entering watch mode with interval=%ss", args.interval)
        try:
            while True:
                try:
                    report = service.run_check(endpoints, quiet=args.quiet)
                except Exception as e:
                    logger.exception("Unexpected error during watch iteration: %s", e)
                time.sleep(max(1, int(args.interval)))
        except KeyboardInterrupt:
            logger.info("Watch mode stopped by user")
            return 0
    else:
        parser.print_help()
        return 2
