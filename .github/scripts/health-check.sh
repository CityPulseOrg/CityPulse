#!/bin/bash
# Health check script for CI pipeline
# Waits for the API to be ready and verifies health endpoint

set -euo pipefail

CONTAINER_NAME="${1:-citypulse-test}"
MAX_ATTEMPTS="${2:-30}"
SLEEP_INTERVAL="${3:-2}"
HEALTH_URL="http://127.0.0.1:8000/health"

echo "Waiting for API to be ready..."

for i in $(seq 1 "$MAX_ATTEMPTS"); do
  if curl -sf "$HEALTH_URL"; then
    echo ""
    echo "Health check passed!"
    exit 0
  fi
  echo "Attempt $i/$MAX_ATTEMPTS - waiting..."
  sleep "$SLEEP_INTERVAL"
done

echo "Health check failed after $MAX_ATTEMPTS attempts"
docker logs "$CONTAINER_NAME"
exit 1
