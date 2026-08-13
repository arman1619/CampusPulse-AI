"""Create the logical PostgreSQL databases used by CampusPulse services.

This command is intended for deployment bootstrap, not normal application requests.
It is idempotent and uses psycopg identifier quoting rather than interpolating SQL names.
"""
from __future__ import annotations

import os
import sys
from urllib.parse import urlsplit, urlunsplit

import psycopg
from psycopg import sql

DATABASES = (
    "campuspulse_auth",
    "campuspulse_feedback",
    "campuspulse_notifications",
    "campuspulse_assistant",
)


def _psycopg_url(url: str) -> str:
    """Convert SQLAlchemy's postgresql+psycopg URL into a psycopg-compatible URL."""
    return url.replace("postgresql+psycopg://", "postgresql://", 1)


def bootstrap(admin_url: str) -> None:
    with psycopg.connect(_psycopg_url(admin_url), autocommit=True) as connection:
        with connection.cursor() as cursor:
            for database in DATABASES:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
                if cursor.fetchone():
                    print(f"database exists: {database}")
                    continue
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database)))
                print(f"database created: {database}")


def main() -> int:
    admin_url = os.getenv("POSTGRES_ADMIN_URL", "").strip()
    if not admin_url:
        print("POSTGRES_ADMIN_URL is required", file=sys.stderr)
        return 2
    bootstrap(admin_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
