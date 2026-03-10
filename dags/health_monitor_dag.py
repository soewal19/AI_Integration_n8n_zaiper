from datetime import datetime, timedelta
import os
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator


def run_health_check():
    from monitoring_service.src.presentation.cli import build_service
    root = Path(__file__).resolve().parents[1]
    service, endpoints = build_service(root)
    report = service.run_check(endpoints, quiet=False)
    failed = sum(1 for r in report.results if r.status == "failed")
    if failed:
        raise RuntimeError(f"Health check failed for {failed} endpoints")


with DAG(
    dag_id="health_monitor_dag",
    schedule_interval="*/15 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={
        "retries": 0,
        "retry_delay": timedelta(minutes=1),
    },
) as dag:
    task = PythonOperator(
        task_id="health_check",
        python_callable=run_health_check,
    )

