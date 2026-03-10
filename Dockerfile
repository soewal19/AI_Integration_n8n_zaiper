FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# No external deps required; copy source
COPY monitoring_service /app/monitoring_service
COPY config /app/config
COPY monitor.py /app/monitor.py

# Health report will be written to /app/health_report.json

ENV SLACK_WEBHOOK_URL=""

CMD ["python", "monitor.py", "--check"]

