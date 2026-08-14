#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for service in auth-service feedback-service ai-service notification-service assistant-service; do
  echo "== $service =="
  (cd "$ROOT/services/$service" && PYTHONPATH=. pytest --cov=app --cov-report=term-missing)
done
if [ -d "$ROOT/frontend/node_modules" ]; then
  (cd "$ROOT/frontend" && npm test && npm run build)
else
  echo "Frontend dependencies not installed; run npm install in frontend before frontend tests."
fi
