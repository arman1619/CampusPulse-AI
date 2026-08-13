#!/usr/bin/env bash
set -euo pipefail
PROJECT="${1:?CodeBuild project name required}"
: "${AWS_REGION:?AWS_REGION required}"
BUILD_ID=$(aws codebuild start-build --project-name "$PROJECT" --region "$AWS_REGION" --query 'build.id' --output text)
echo "Started CodeBuild verification: $BUILD_ID"
while true; do
  STATUS=$(aws codebuild batch-get-builds --ids "$BUILD_ID" --region "$AWS_REGION" --query 'builds[0].buildStatus' --output text)
  echo "CodeBuild status: $STATUS"
  case "$STATUS" in
    SUCCEEDED) exit 0 ;;
    FAILED|FAULT|STOPPED|TIMED_OUT) exit 1 ;;
  esac
  sleep 10
done
