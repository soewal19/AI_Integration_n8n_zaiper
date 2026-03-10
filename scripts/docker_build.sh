#!/usr/bin/env bash
set -euo pipefail
IMAGE_NAME="${1:-health-monitor}"
docker build -t "$IMAGE_NAME" .

