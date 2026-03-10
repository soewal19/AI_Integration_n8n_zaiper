#!/usr/bin/env bash
set -euo pipefail
IMAGE_NAME="${1:-health-monitor}"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
docker run --rm -e SLACK_WEBHOOK_URL="$SLACK_WEBHOOK_URL" "$IMAGE_NAME"

