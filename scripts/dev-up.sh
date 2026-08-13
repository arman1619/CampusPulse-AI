#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
command -v docker >/dev/null || { echo "Docker is required."; exit 1; }
[ -f .env ] || cp .env.example .env
BACKEND="$(grep '^ASSISTANT_BACKEND=' .env 2>/dev/null | tail -1 | cut -d= -f2- || true)"
TOKEN="$(grep '^HF_TOKEN=' .env 2>/dev/null | tail -1 | cut -d= -f2- || true)"
if [ "${BACKEND:-huggingface}" != "template" ] && [ -z "$TOKEN" ]; then
  echo "HF_TOKEN is not configured. Run ./scripts/set-hf-token.sh, then run dev-up.sh again." >&2
  exit 1
fi
echo "Starting CampusPulse AI..."
docker compose up --build -d
python scripts/wait_for_stack.py --url http://localhost:8080 --timeout 240
python scripts/seed_demo.py || echo "Demo issue seeding skipped; demo users are still created by auth-service."
echo "CampusPulse AI: http://localhost:8080"
echo "Grafana optional: docker compose -f docker-compose.yml -f docker-compose.observability.yml up -d prometheus grafana"
