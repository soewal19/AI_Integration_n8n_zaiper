# Интеграция с Apache Airflow

Этот документ описывает, как запускать мониторинг через Airflow: переменные/коннекшены, деплой через Helm (Kubernetes) и через Google Cloud Composer.

## 1) DAG
- Файл DAG: `dags/health_monitor_dag.py`
- Cron: `*/15 * * * *` — каждые 15 минут.
- Поведение: если есть хотя бы один `failed`, task падает (Airflow отправит уведомление согласно вашим настройкам).

## 2) Переменные и секреты
Сервис читает следующие переменные окружения:
- `SLACK_WEBHOOK_URL` — вебхук Slack.
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — для Telegram (опционально).
- `CONFIG_PATH` — путь к `endpoints.json` (по умолчанию `config/endpoints.json`).
- `DB_PATH` — путь к SQLite (по умолчанию `monitoring_service/health_history.db`).
- `LOG_LEVEL` — уровень логов (INFO по умолчанию).

### Через Airflow Variables / CLI
Локально (airflow CLI в среде):
```bash
airflow variables set SLACK_WEBHOOK_URL https://hooks.slack.com/...
airflow variables set CONFIG_PATH /opt/airflow/dags/repo/config/endpoints.json
airflow variables set DB_PATH /opt/airflow/data/health_history.db
airflow variables set LOG_LEVEL INFO
```
> Переменные доступны из Python, если вы их читаете через Airflow API. В нашем сервисе переменные берутся из env. Рекомендуется прокидывать значения как env (см. Helm/Composer ниже).

## 3) Деплой через Helm (официальный чарт Apache Airflow)
Рекомендуем хранить секреты в Kubernetes Secrets и прокидывать их в Airflow как env.

### 3.1 Создать секреты
Готовый шаблон: `deploy/k8s/secrets.example.yaml`
```
kubectl apply -n airflow -f deploy/k8s/secrets.example.yaml
```

### 3.2 Пример values.yaml
Шаблон: `deploy/k8s/values.example.yaml`
> PVC для `/opt/airflow/data` нужен, если хотите сохранять SQLite между подами. Иначе используйте внешний репозиторий (например, Postgres) — реализуйте другой `ResultsRepository`.

### 3.3 Установка
```bash
helm repo add apache-airflow https://airflow.apache.org
helm upgrade --install airflow apache-airflow/airflow -f values.yaml -n airflow --create-namespace
```

### 3.4 Job‑инициализатор переменных
Шаблон: `deploy/k8s/job-airflow-init.yaml`
```
kubectl apply -n airflow -f deploy/k8s/job-airflow-init.yaml
```
Job выполнит `airflow variables set ...` внутри контейнера Airflow.

## 4) Google Cloud Composer
Для Composer v2:

### 4.1 Загрузка DAG’а
Скопируйте содержимое репозитория (или только папку `dags`) в GCS‑бакет Composer’а:
```
gsutil -m rsync -r ./dags gs://<COMPOSER_BUCKET>/dags
gsutil -m rsync -r ./config gs://<COMPOSER_BUCKET>/dags/repo/config
```

### 4.2 Переменные окружения
В Composer используйте `gcloud composer environments update`:
```bash
gcloud composer environments update <ENV_NAME> \
  --location <REGION> \
  --update-env-variables \
  SLACK_WEBHOOK_URL=https://hooks.slack.com/...,CONFIG_PATH=/opt/airflow/dags/repo/config/endpoints.json,DB_PATH=/opt/airflow/data/health_history.db,LOG_LEVEL=INFO
```

### 4.3 Переменные Airflow (альтернативно)
```bash
gcloud composer environments run <ENV_NAME> --location <REGION> variables -- \
  set SLACK_WEBHOOK_URL https://hooks.slack.com/...
gcloud composer environments run <ENV_NAME> --location <REGION> variables -- \
  set CONFIG_PATH /opt/airflow/dags/repo/config/endpoints.json
gcloud composer environments run <ENV_NAME> --location <REGION> variables -- \
  set DB_PATH /opt/airflow/data/health_history.db
gcloud composer environments run <ENV_NAME> --location <REGION> variables -- \
  set LOG_LEVEL INFO
```
> Рекомендуется использовать env‑переменные на уровне окружения, чтобы сервис читал их напрямую.

### 4.4 Хранение секретов
- В Composer секреты обычно задают как env‑переменные окружения (см. 4.2). Альтернатива — хранить в Airflow Variables и читать в задаче.

## 5) Запуск и мониторинг
- Включите DAG `health_monitor_dag` в UI Airflow.
- При наличии failed task завершится с ошибкой — проверьте логи task и сообщение в Slack/Telegram.
- Для кастомной логики эскалации добавьте в DAG ретраи/Branch/EmailOperator и т.п.

## 6) Советы по продакшену
- Не храните секреты в репозитории. Используйте Kubernetes Secrets / Composer env.
- SQLite подходит как журнал для демо/PoC. В проде используйте внешнюю БД и реализуйте `ResultsRepository` под Postgres.
- Для больших списков эндпоинтов используйте шардинг по задачам (например, группа задач с разбиением endpoints.json).
