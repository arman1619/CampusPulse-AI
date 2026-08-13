#!/usr/bin/env bash
set -euo pipefail
TAG="${1:?image tag required}"
: "${AWS_ACCOUNT_ID:?AWS_ACCOUNT_ID required}"
: "${AWS_REGION:?AWS_REGION required}"
REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$REGISTRY"
for pair in "frontend:frontend" "gateway:gateway" "auth-service:auth" "feedback-service:feedback" "ai-service:ai" "notification-service:notification" "assistant-service:assistant"; do
  local_name="${pair%%:*}"
  repo="campuspulse-${pair##*:}"
  docker tag "campuspulse-ai-${local_name}:${TAG}" "$REGISTRY/$repo:$TAG"
  docker push "$REGISTRY/$repo:$TAG"
done
