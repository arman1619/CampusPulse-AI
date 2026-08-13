#!/usr/bin/env bash
set -euo pipefail
TAG="${1:?image tag required}";TARGET_ENV="${2:?inactive EB environment required}";: "${AWS_REGION:?AWS_REGION required}";: "${EB_APPLICATION:?EB_APPLICATION required}";: "${EB_ARTIFACT_BUCKET:?EB_ARTIFACT_BUCKET required}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)";ZIP="$ROOT/dist/campuspulse-eb-$TAG.zip";[ -f "$ZIP" ] || "$ROOT/infrastructure/aws/package-eb.sh" "$TAG"
KEY="releases/campuspulse-eb-$TAG.zip";VERSION="campuspulse-$TAG"
aws s3 cp "$ZIP" "s3://$EB_ARTIFACT_BUCKET/$KEY" --region "$AWS_REGION"
aws elasticbeanstalk create-application-version --application-name "$EB_APPLICATION" --version-label "$VERSION" --source-bundle S3Bucket="$EB_ARTIFACT_BUCKET",S3Key="$KEY" --region "$AWS_REGION"
aws elasticbeanstalk update-environment --environment-name "$TARGET_ENV" --version-label "$VERSION" --region "$AWS_REGION"
aws elasticbeanstalk wait environment-updated --environment-names "$TARGET_ENV" --region "$AWS_REGION"
echo "Inactive environment updated. Run smoke tests before any CNAME swap."
