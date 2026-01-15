#!/bin/bash
# Entrypoint script for CityPulse backend
# Runs database migrations before starting the application

set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
