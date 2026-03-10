#!/usr/bin/env bash
set -euo pipefail

# CI/CD deployment script example
# 1) Run tests
python -m unittest discover -s tests -p "test_*.py" -v

# 2) Build Docker image
IMAGE_NAME="${IMAGE_NAME:-health-monitor}"
docker build -t "$IMAGE_NAME" .

# 3) Optional: Push to registry (expects DOCKER_REGISTRY, DOCKER_USERNAME, DOCKER_PASSWORD)
if [[ -n "${DOCKER_REGISTRY:-}" && -n "${DOCKER_USERNAME:-}" && -n "${DOCKER_PASSWORD:-}" ]]; then
  echo "$DOCKER_PASSWORD" | docker login "$DOCKER_REGISTRY" -u "$DOCKER_USERNAME" --password-stdin
  docker tag "$IMAGE_NAME" "$DOCKER_REGISTRY/$IMAGE_NAME:latest"
  docker push "$DOCKER_REGISTRY/$IMAGE_NAME:latest"
fi

