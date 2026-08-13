param([Parameter(Mandatory=$true)][string]$Tag)
$ErrorActionPreference = "Stop"
if (-not $env:AWS_ACCOUNT_ID) { throw "AWS_ACCOUNT_ID required" }
if (-not $env:AWS_REGION) { throw "AWS_REGION required" }
$Registry = "$($env:AWS_ACCOUNT_ID).dkr.ecr.$($env:AWS_REGION).amazonaws.com"
aws ecr get-login-password --region $env:AWS_REGION | docker login --username AWS --password-stdin $Registry
$Map = @{
  "campuspulse-ai-frontend"="campuspulse-frontend"; "campuspulse-ai-gateway"="campuspulse-gateway";
  "campuspulse-ai-auth-service"="campuspulse-auth"; "campuspulse-ai-feedback-service"="campuspulse-feedback";
  "campuspulse-ai-ai-service"="campuspulse-ai"; "campuspulse-ai-notification-service"="campuspulse-notification";
  "campuspulse-ai-assistant-service"="campuspulse-assistant"
}
foreach ($Local in $Map.Keys) {
  $Remote = "$Registry/$($Map[$Local]):$Tag"
  docker tag "$Local`:latest" $Remote
  docker push $Remote
}
