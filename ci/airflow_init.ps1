$env:SLACK_WEBHOOK_URL = $env:SLACK_WEBHOOK_URL
$env:CONFIG_PATH = $env:CONFIG_PATH
$env:DB_PATH = $env:DB_PATH
$env:LOG_LEVEL = $env:LOG_LEVEL

airflow variables set SLACK_WEBHOOK_URL ($env:SLACK_WEBHOOK_URL)
airflow variables set CONFIG_PATH ($env:CONFIG_PATH -ne $null ? $env:CONFIG_PATH : "/opt/airflow/dags/repo/config/endpoints.json")
airflow variables set DB_PATH ($env:DB_PATH -ne $null ? $env:DB_PATH : "/opt/airflow/data/health_history.db")
airflow variables set LOG_LEVEL ($env:LOG_LEVEL -ne $null ? $env:LOG_LEVEL : "INFO")

