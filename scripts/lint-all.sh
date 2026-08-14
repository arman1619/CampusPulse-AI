#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

for service in auth-service feedback-service ai-service notification-service assistant-service; do
  (cd "$ROOT/services/$service" && ruff check app tests --select E9,F63,F7,F82)
done

if [ -d "$ROOT/frontend/node_modules" ]; then
  (cd "$ROOT/frontend" && npm run lint)
fi
