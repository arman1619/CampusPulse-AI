#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python scripts/release_check.py
python scripts/write_release_manifest.py
python scripts/package_release.py
