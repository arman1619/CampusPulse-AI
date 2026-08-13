#!/usr/bin/env bash
set -euo pipefail
TAG="${1:?image tag required}"
: "${AWS_ACCOUNT_ID:?AWS_ACCOUNT_ID required}"
: "${AWS_REGION:?AWS_REGION required}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/dist/eb-$TAG"
rm -rf "$OUT" && mkdir -p "$OUT"
export IMAGE_TAG="$TAG"
# Only immutable image coordinates are expanded. All application environment variables,
# including EB_LOG_BASE_DIR and Secrets Manager-provided values, remain runtime variables.
envsubst '${AWS_ACCOUNT_ID} ${AWS_REGION} ${IMAGE_TAG}' \
  < "$ROOT/infrastructure/aws/docker-compose.aws.yml.tpl" \
  > "$OUT/docker-compose.yml"
(cd "$OUT" && zip -q "../campuspulse-eb-$TAG.zip" docker-compose.yml)
echo "$ROOT/dist/campuspulse-eb-$TAG.zip"
