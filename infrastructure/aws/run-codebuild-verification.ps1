param([Parameter(Mandatory=$true)][string]$ProjectName)
$ErrorActionPreference = "Stop"
if (-not $env:AWS_REGION) { throw "AWS_REGION required" }
$BuildId = aws codebuild start-build --project-name $ProjectName --region $env:AWS_REGION --query 'build.id' --output text
Write-Host "Started CodeBuild: $BuildId"
do {
  Start-Sleep -Seconds 10
  $Status = aws codebuild batch-get-builds --ids $BuildId --region $env:AWS_REGION --query 'builds[0].buildStatus' --output text
  Write-Host "CodeBuild status: $Status"
} while ($Status -in @('IN_PROGRESS'))
if ($Status -ne 'SUCCEEDED') { throw "CodeBuild verification failed: $Status" }
