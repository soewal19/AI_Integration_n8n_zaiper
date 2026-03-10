#!/usr/bin/env bash
set -euo pipefail

# Initialize Airflow Variables from env (run inside Airflow container or with AIRFLOW_HOME configured)
airflow variables set SLACK_WEBHOOK_URL "${SLACK_WEBHOOK_URL:-}"
airflow variables set CONFIG_PATH "${CONFIG_PATH:-/opt/airflow/dags/repo/config/endpoints.json}"
airflow variables set DB_PATH "${DB_PATH:-/opt/airflow/data/health_history.db}"
airflow variables set LOG_LEVEL "${LOG_LEVEL:-INFO}"

