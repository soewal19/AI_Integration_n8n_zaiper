# Monitoring Service — Health Check + Slack Alerts

Сервис мониторинга внешних API на Python:
- параллельно проверяет эндпоинты;
- измеряет время ответа и статус;
- пишет отчет в `health_report.json` и историю в SQLite;
- отправляет алерты в Slack или печатает в консоль.

## Ссылка на репозиторий
- GitHub: [soewal19/AI_Integration_n8n_zaiper](https://github.com/soewal19/AI_Integration_n8n_zaiper)

## Стек
- Python 3.10+
- Стандартная библиотека: `concurrent.futures`, `urllib.request`, `sqlite3`, `logging`

## Быстрый старт
1. Откройте [config/endpoints.json](file:///e:/TestTask/AI%20Integration_n8n_zaiper/config/endpoints.json) и проверьте список эндпоинтов.
2. Скопируйте пример переменных окружения:
   - `cp config/settings.env.example config/settings.env`
3. При необходимости задайте `SLACK_WEBHOOK_URL` в `config/settings.env` или через переменную окружения.

## Запуск
```bash
python monitor.py --check           # одна проверка
python monitor.py --watch           # бесконечный цикл, интервал 60 сек
python monitor.py --check --quiet   # без отправки в Slack (только консоль)
python monitor.py --watch --interval 120  # интервал в секундах
```
Коды выхода: `0` — успех, `1` — есть ошибки, `2` — неверные аргументы.

Также доступна точка входа [main.py](file:///e:/TestTask/AI%20Integration_n8n_zaiper/main.py), которая вызывает тот же CLI.

## Конфигурация (12‑Factor)
Файл `config/settings.env` может содержать:
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
DB_PATH=monitoring_service/health_history.db
CONFIG_PATH=config/endpoints.json
LOG_LEVEL=INFO
```
- Файл автоматически подгружается при старте.
- `DB_PATH` и `CONFIG_PATH` можно переопределить переменными окружения.
- `LOG_LEVEL`: DEBUG/INFO/WARNING/ERROR/CRITICAL.

## Как это работает
- Параллельные проверки — `ThreadPoolExecutor`.
- Таймаут на запрос — 5 секунд.
- `status = "failed"` если:
  - статус не совпадает с ожидаемым;
  - время ответа ≥ 2000ms;
  - ошибка соединения/таймаут.
- Контроллер [MonitoringService](file:///e:/TestTask/AI%20Integration_n8n_zaiper/monitoring_service/src/application/services.py) оркестрирует проверку, запись отчета и алерт.
- История в SQLite: [database.py](file:///e:/TestTask/AI%20Integration_n8n_zaiper/monitoring_service/src/infrastructure/database.py).

## Логирование
- Формат: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`
- Уровень регулируется `LOG_LEVEL` (по умолчанию INFO).

## Сценарии (DevOps)
- PowerShell: [scripts/run_check.ps1](file:///e:/TestTask/AI%20Integration_n8n_zaiper/scripts/run_check.ps1), [scripts/watch.ps1](file:///e:/TestTask/AI%20Integration_n8n_zaiper/scripts/watch.ps1)
- Bash: [scripts/run_check.sh](file:///e:/TestTask/AI%20Integration_n8n_zaiper/scripts/run_check.sh), [scripts/watch.sh](file:///e:/TestTask/AI%20Integration_n8n_zaiper/scripts/watch.sh)
- Docker:
  - Сборка: `./scripts/docker_build.sh health-monitor`
  - Запуск: `SLACK_WEBHOOK_URL=... ./scripts/docker_run.sh health-monitor`
- CI/CD:
  - Скрипт деплоя: [ci/deploy.sh](file:///e:/TestTask/AI%20Integration_n8n_zaiper/ci/deploy.sh), [ci/deploy.ps1](file:///e:/TestTask/AI%20Integration_n8n_zaiper/ci/deploy.ps1)
  - GitHub Actions: [.github/workflows/ci.yml](file:///e:/TestTask/AI%20Integration_n8n_zaiper/.github/workflows/ci.yml)
- Dev‑зависимости (локально для линтеров/типов):
  ```bash
  python -m pip install -r requirements-dev.txt
  ```
- Публикация в GitHub: [docs/DEPLOY_GITHUB.md](file:///e:/TestTask/AI%20Integration_n8n_zaiper/docs/DEPLOY_GITHUB.md)

## Тесты
- E2E: `python -m unittest discover -s tests -p "test_*.py" -v`
- Скрипты: [scripts/test_e2e.ps1](file:///e:/TestTask/AI%20Integration_n8n_zaiper/scripts/test_e2e.ps1), [scripts/test_e2e.sh](file:///e:/TestTask/AI%20Integration_n8n_zaiper/scripts/test_e2e.sh)

## Структура
```
monitoring_service/
  src/
    domain/               # Доменные модели
    application/          # Сервисы / use-cases
    infrastructure/       # HTTP, notifier, SQLite, config
    presentation/         # CLI
config/
  endpoints.json
  settings.env(.example)
docs/
  C4.md                  # C4-модель (общая)
  C4_db.md               # C4-модель (углубление по БД)
monitor.py               # Точка входа (CLI)
main.py                  # Альтернативная точка входа
health_report.json       # Отчет (создается во время работы)
```

## Архитектура (C4)
- См. [docs/C4.md](file:///e:/TestTask/AI%20Integration_n8n_zaiper/docs/C4.md) и [docs/C4_db.md](file:///e:/TestTask/AI%20Integration_n8n_zaiper/docs/C4_db.md)
- Слои: Domain → Application → Infrastructure → Presentation (Clean Architecture).

## Практики DevOps
- Контейнеризация: Dockerfile, `.dockerignore`.
- Наблюдаемость: JSON‑отчет, логирование.
- Надежность: коды выхода для Airflow/CI.
- Конфигурация: `settings.env` + переменные окружения.
- Кроссплатформенность: скрипты для Windows и Linux/macOS.

## Дополнения
- Pydantic‑модели: [entities_pyd.py](file:///e:/TestTask/AI%20Integration_n8n_zaiper/monitoring_service/src/domain/entities_pyd.py) как опциональная строгая валидация.
- Airflow DAG: [dags/health_monitor_dag.py](file:///e:/TestTask/AI%20Integration_n8n_zaiper/dags/health_monitor_dag.py) с cron `*/15 * * * *`.
- Telegram Notifier: [notifier_telegram.py](file:///e:/TestTask/AI%20Integration_n8n_zaiper/monitoring_service/src/infrastructure/notifier_telegram.py) с переменными `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
- Подробное описание проекта: [docs/PROJECT.md](file:///e:/TestTask/AI%20Integration_n8n_zaiper/docs/PROJECT.md)
- Интеграция с Airflow: [docs/AIRFLOW.md](file:///e:/TestTask/AI%20Integration_n8n_zaiper/docs/AIRFLOW.md)
- Зависимости и установка: [docs/DEPENDENCIES.md](file:///e:/TestTask/AI%20Integration_n8n_zaiper/docs/DEPENDENCIES.md)

## Примечание по Agent Engineering
- MonitoringService уже выступает «агентом‑координатором», делегирующим задачи подсистемам (HTTP‑проверка, репозиторий, нотификации).
- Отдельные «AI‑агенты» здесь не требуются. При необходимости легко добавить независимый компонент (например, стратегию уведомлений или адаптивные политики ретраев) через расширение интерфейсов без изменения основной логики.

## Архитектурные принципы (проверка)
- Clean Architecture: соблюдено разделение на слои (Domain, Application, Infrastructure, Presentation). Зависимости направлены внутрь, композиция делается в CLI.
- SOLID:
  - S (Single Responsibility) — Checker проверяет HTTP, Notifier уведомляет, Repo сохраняет, Service оркестрирует.
  - O (Open/Closed) — легко добавить TelegramNotifier/PostgresRepo, не меняя Application‑слой.
  - D (Dependency Inversion) — Application зависит от интерфейсов (HTTPChecker, Notifier, ResultsRepository).
- MVC соответствие:
  - Model — доменные сущности (dataclasses) и SQLite‑репозиторий.
  - View — Slack/Console Notifier и JSON‑отчет.
  - Controller — MonitoringService.
- Pydantic: в текущей реализации сущности — dataclasses стандартной библиотеки (минимум зависимостей). При необходимости можно заменить на Pydantic без изменения бизнес‑логики.
- Agent Engineering: MonitoringService — «агент»‑координатор, подсистемы изолированы и связаны через интерфейсы.

Английская версия: см. [README_EN.md](file:///e:/TestTask/AI%20Integration_n8n_zaiper/README_EN.md)
