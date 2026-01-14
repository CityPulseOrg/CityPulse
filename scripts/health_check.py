#!/usr/bin/env python3
"""
Health check script for the CityPulse container.
Verifies the container is running and responsive.
"""
import argparse
import subprocess
import sys
import time
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

DEFAULT_CONTAINER_NAME = "citypulse-test"
MAX_RETRIES = 30
RETRY_DELAY = 2


def check_container_running(container_name: str) -> bool:
    """Check if the container is running."""
    result = subprocess.run(
        ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    return container_name in result.stdout


def get_container_logs(container_name: str) -> str:
    """Get container logs for debugging."""
    result = subprocess.run(
        ["docker", "logs", container_name],
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


def health_check(container_name: str) -> bool:
    """Wait for container to start and verify it's healthy."""
    print(f"Waiting for container '{container_name}' to start...")

    for attempt in range(MAX_RETRIES):
        time.sleep(RETRY_DELAY)
        if check_container_running(container_name):
            print(f"Container is running (attempt {attempt + 1})")
            break
        print(f"Container not ready, retrying... ({attempt + 1}/{MAX_RETRIES})")

    if not check_container_running(container_name):
        print("::error::Container failed to start")
        print("Container logs:")
        print(get_container_logs(container_name))
        return False

    # Poll the API health endpoint published at localhost:8000/health
    print("Checking API health at http://localhost:8000/health ...")
    for attempt in range(MAX_RETRIES):
        try:
            with urlopen("http://localhost:8000/health", timeout=3) as resp:
                if resp.status == 200:
                    payload = json.loads(resp.read().decode("utf-8"))
                    status = payload.get("status")
                    db_status = payload.get("database")
                    if status == "healthy" and db_status in (None, "ok"):
                        print("API health OK")
                        return True
                    else:
                        print(f"Health response indicates issue: {payload}")
        except (URLError, HTTPError) as e:
            pass
        time.sleep(RETRY_DELAY)
        print(f"API not healthy yet, retrying... ({attempt + 1}/{MAX_RETRIES})")

    print("::error::API health check failed")
    print("Container logs:")
    print(get_container_logs(container_name))
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Health check for CityPulse container")
    parser.add_argument("container_name", nargs="?", default=DEFAULT_CONTAINER_NAME,
                        help=f"Container name (default: {DEFAULT_CONTAINER_NAME})")
    args = parser.parse_args()
    sys.exit(0 if health_check(args.container_name) else 1)
