#!/bin/bash
# Verify required secrets are injected into the container
set -euo pipefail

CONTAINER_NAME="${1:-citypulse-test}"

echo "Verifying secrets are injected..."

docker exec "$CONTAINER_NAME" sh -c '
  if [ -z "$BACKBOARD_API_KEY" ]; then
    echo "ERROR: BACKBOARD_API_KEY is not set"
    exit 1
  fi
  echo "BACKBOARD_API_KEY is set"
'

echo "All secrets verified."
