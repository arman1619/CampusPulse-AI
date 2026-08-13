#!/usr/bin/env bash
set -euo pipefail
TAG="${1:?git SHA/release tag required}"
for svc in auth-service feedback-service ai-service notification-service assistant-service frontend gateway; do
  docker tag "campuspulse-ai-${svc}:latest" "campuspulse-ai-${svc}:${TAG}"
done
