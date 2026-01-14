#!/usr/bin/env python3
"""
Verify that all required secrets/environment variables are configured.
Used in CI to fail fast if secrets are missing.
"""
import argparse
import os
import subprocess
import sys

REQUIRED_SECRETS = [
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "BACKBOARD_API_KEY",
    "VITE_API_URL",
]

CONTAINER_SECRETS = [
    "BACKBOARD_API_KEY",
]


def verify_secrets() -> bool:
    """Check that all required environment variables are set."""
    missing = []
    for secret in REQUIRED_SECRETS:
        if not os.environ.get(secret):
            missing.append(secret)

    if missing:
        print(f"::error::Missing required secrets: {', '.join(missing)}")
        return False

    print("All required secrets are configured")
    return True


def verify_container_secrets(container_name: str) -> bool:
    """Check that required secrets are injected into the container."""
    print(f"Verifying secrets are injected into '{container_name}'...")
    missing = []

    for secret in CONTAINER_SECRETS:
        result = subprocess.run(
            ["docker", "exec", container_name, "sh", "-c", f'test -n "${{{secret}}}"'],
            capture_output=True,
        )
        if result.returncode != 0:
            missing.append(secret)
        else:
            print(f"{secret} is set")

    if missing:
        print(f"::error::Missing secrets in container: {', '.join(missing)}")
        return False

    print("All secrets verified.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify secrets configuration")
    parser.add_argument("--container", metavar="NAME",
                        help="Check secrets inside a running container")
    args = parser.parse_args()

    if args.container:
        sys.exit(0 if verify_container_secrets(args.container) else 1)
    else:
        sys.exit(0 if verify_secrets() else 1)
