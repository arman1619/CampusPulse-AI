#!/usr/bin/env bash
set -euo pipefail
: "${AWS_REGION:?AWS_REGION is required}";: "${EB_BLUE_ENV:?EB_BLUE_ENV is required}";: "${EB_GREEN_ENV:?EB_GREEN_ENV is required}"
ACTIVE="${1:-$EB_BLUE_ENV}";PREVIOUS="${2:-$EB_GREEN_ENV}"
echo "Swapping CNAMEs to return traffic from $ACTIVE to $PREVIOUS"
aws elasticbeanstalk swap-environment-cnames --region "$AWS_REGION" --source-environment-name "$ACTIVE" --destination-environment-name "$PREVIOUS"
aws elasticbeanstalk wait environment-updated --region "$AWS_REGION" --environment-names "$PREVIOUS" || true
