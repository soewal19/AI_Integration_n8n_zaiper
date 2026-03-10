# Monitoring Service — Health Check + Slack Alerts

Python service for monitoring external APIs:
- runs parallel endpoint checks;
- measures response time and status;
- writes a report to `health_report.json` and history to SQLite;
- sends alerts to Slack or prints to console.

## Stack
- Python 3.10+
- Standard library only: `concurrent.futures`, `urllib.request`, `sqlite3`, `logging`

## Quick Start
1. Review endpoints in [config/endpoints.json](file:///e:/TestTask/AI%20Integration_n8n_zaiper/config/endpoints.json).
2. Copy env example:
   - `cp config/settings.env.example config/settings.env`
3. Optionally set `SLACK_WEBHOOK_URL` in `config/settings.env` or via environment.

## Run
```bash
python monitor.py --check           # single check
python monitor.py --watch           # loop, default interval 60s
python monitor.py --check --quiet   # no Slack, console only
python monitor.py --watch --interval 120
```
Exit codes: `0` — success, `1` — failures present, `2` — invalid arguments.

Alternate entry point [main.py](file:///e:/TestTask/AI%20Integration_n8n_zaiper/main.py) calls the same CLI.

## Configuration (12‑Factor)
`config/settings.env`:
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
DB_PATH=monitoring_service/health_history.db
CONFIG_PATH=config/endpoints.json
LOG_LEVEL=INFO
```
- File is auto‑loaded on startup.
- `DB_PATH` and `CONFIG_PATH` can be overridden by env variables.
- `LOG_LEVEL`: DEBUG/INFO/WARNING/ERROR/CRITICAL.

## How It Works
- Parallel checks — `ThreadPoolExecutor`.
- Per‑request timeout — 5 seconds.
- `status = "failed"` when:
  - actual status != expected;
  - response time ≥ 2000ms;
  - connection error/timeout.
- Controller [MonitoringService](file:///e:/TestTask/AI%20Integration_n8n_zaiper/monitoring_service/src/application/services.py) orchestrates checks, report and alert.
- SQLite history: [database.py](file:///e:/TestTask/AI%20Integration_n8n_zaiper/monitoring_service/src/infrastructure/database.py).

## Logging
- Format: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`
- Level via `LOG_LEVEL` (default INFO).

## DevOps
- PowerShell: [scripts/run_check.ps1](file:///e:/TestTask/AI%20Integration_n8n_zaiper/scripts/run_check.ps1), [scripts/watch.ps1](file:///e:/TestTask/AI%20Integration_n8n_zaiper/scripts/watch.ps1)
- Bash: [scripts/run_check.sh](file:///e:/TestTask/AI%20Integration_n8n_zaiper/scripts/run_check.sh), [scripts/watch.sh](file:///e:/TestTask/AI%20Integration_n8n_zaiper/scripts/watch.sh)
- Docker:
  - Build: `./scripts/docker_build.sh health-monitor`
  - Run: `SLACK_WEBHOOK_URL=... ./scripts/docker_run.sh health-monitor`
- CI/CD:
  - Deploy scripts: [ci/deploy.sh](file:///e:/TestTask/AI%20Integration_n8n_zaiper/ci/deploy.sh), [ci/deploy.ps1](file:///e:/TestTask/AI%20Integration_n8n_zaiper/ci/deploy.ps1)
  - GitHub Actions: [.github/workflows/ci.yml](file:///e:/TestTask/AI%20Integration_n8n_zaiper/.github/workflows/ci.yml)
- Dev dependencies (local lint/type checks):
  ```bash
  python -m pip install -r requirements-dev.txt
  ```
- Publish to GitHub: [docs/DEPLOY_GITHUB.md](file:///e:/TestTask/AI%20Integration_n8n_zaiper/docs/DEPLOY_GITHUB.md)

## Tests
- E2E: `python -m unittest discover -s tests -p "test_*.py" -v`

## Structure
```
monitoring_service/
  src/
    domain/               # Domain models
    application/          # Services / use-cases
    infrastructure/       # HTTP, notifier, SQLite, config
    presentation/         # CLI
config/
  endpoints.json
  settings.env(.example)
docs/
  C4.md                  # C4 (overview)
  C4_db.md               # C4 (data layer deep dive)
  PROJECT.md             # Detailed project description
monitor.py               # CLI entry
main.py                  # Alternate entry
health_report.json       # Report (created at runtime)
```

## Architecture & Patterns
- Clean Architecture: clear separation — Domain, Application, Infrastructure, Presentation; dependencies point inward.
- SOLID:
  - Single Responsibility — each component does one thing (Checker, Notifier, Repo).
  - Open/Closed — add TelegramNotifier or PostgresRepo without changing core logic.
  - Dependency Inversion — Application depends on interfaces, not implementations.
- MVC Mapping:
  - Model — entities (dataclasses) and repository (SQLite).
  - View — notifier (Slack/Console) and JSON reporter.
  - Controller — MonitoringService.
- Agent Engineering:
  - MonitoringService acts as a coordinator agent delegating to specialized subsystems.

Note on Pydantic: entities are implemented with Python dataclasses for zero‑dependency runtime. Switching to Pydantic is straightforward if strict validation is required.

