# Проект: Monitoring Service

## Назначение
Сервис мониторит внешние API: параллельно проверяет доступность, валидирует статус‑коды и задержки, пишет отчеты и присылает алерты в Slack/Telegram. Предназначен для интеграции с оркестраторами (Airflow/CI) и встраивания в существующие бэкенд‑потоки.

## Архитектура
- Clean Architecture: Domain, Application, Infrastructure, Presentation.
- DIP: Application зависит от интерфейсов (HTTPChecker, Notifier, ResultsRepository); конкретные реализации внедряются в composition root.
- SoC: Данные, логика, инфраструктура и представление разделены.
- MVC Mapping: Model (сущности и Repo), View (Notifier, JSON‑отчет), Controller (MonitoringService).
- Agent Engineering: MonitoringService координирует специализированные подсистемы.

## Технологии
- Python 3.10+, стандартная библиотека (urllib.request, sqlite3, concurrent.futures, logging).
- SQLite для истории результатов.
- Slack/Telegram для уведомлений через HTTP‑вебхуки.
- Docker для упаковки, GitHub Actions для CI.

## Основные компоненты
- Domain: entities.py — доменные сущности; entities_pyd.py — опциональные Pydantic‑модели.
- Application: services.py — сценарий проверки; interfaces.py — абстракции.
- Infrastructure: http_client.py — параллельные HTTP‑проверки; database.py — SQLite‑репозиторий; notifiers.py — Slack/console; notifier_telegram.py — Telegram.
- Presentation: cli.py — CLI и композиция зависимостей.
- Airflow: dags/health_monitor_dag.py — DAG с cron */15 * * * *.

## Настройка
- config/endpoints.json — список эндпоинтов.
- config/settings.env — переменные окружения: SLACK_WEBHOOK_URL, DB_PATH, CONFIG_PATH, LOG_LEVEL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID.

## Сценарии запуска
- Одноразовая проверка: `python monitor.py --check`
- Непрерывный режим: `python monitor.py --watch --interval 60`
- Без Slack: `python monitor.py --check --quiet`
- Docker: `./scripts/docker_build.sh` и `./scripts/docker_run.sh`
- Airflow: подключить репозиторий к AIRFLOW_HOME, активировать DAG `health_monitor_dag`.

## Pydantic‑модели
Файл `entities_pyd.py` содержит Pydantic‑варианты моделей. По умолчанию сервис использует dataclasses. Для строгой валидации можно заменить импорты сущностей на Pydantic‑версии в своих кастомных точках входа, не затрагивая Application‑слой.

## Telegram‑уведомления
Задать `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID`. Подключить `TelegramNotifier` в composition root вместо SlackOrConsoleNotifier при необходимости.

## Масштабирование
- HTTP клиент может быть заменён на httpx/requests.
- SQLite легко заменить на Postgres, реализовав новый ResultsRepository.
- Добавление новых каналов уведомлений делается через реализацию Notifier.

