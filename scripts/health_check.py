#!/usr/bin/env python3
"""
Health check script for the CityPulse container.
Verifies the container is running and responsive.
"""
import argparse
import subprocess
import sys
import time

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
            return True
        print(f"Container not ready, retrying... ({attempt + 1}/{MAX_RETRIES})")

    print("::error::Container failed to start")
    print("Container logs:")
    print(get_container_logs(container_name))
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Health check for CityPulse container")
    parser.add_argument("container_name", nargs="?", default=DEFAULT_CONTAINER_NAME,
                        help=f"Container name (default: {DEFAULT_CONTAINER_NAME})")
    args = parser.parse_args()
    sys.exit(0 if health_check(args.container_name) else 1)
