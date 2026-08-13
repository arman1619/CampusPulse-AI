param([Parameter(Mandatory=$true)][string]$Tag)
$ErrorActionPreference = "Stop"
if (-not $env:AWS_ACCOUNT_ID) { throw "AWS_ACCOUNT_ID required" }
if (-not $env:AWS_REGION) { throw "AWS_REGION required" }
$Root = Resolve-Path (Join-Path $PSScriptRoot "../..")
$Out = Join-Path $Root "dist/eb-$Tag"
if (Test-Path $Out) { Remove-Item $Out -Recurse -Force }
New-Item -ItemType Directory -Path $Out | Out-Null
$Template = Get-Content (Join-Path $Root "infrastructure/aws/docker-compose.aws.yml.tpl") -Raw
$Rendered = $Template.Replace('${AWS_ACCOUNT_ID}', $env:AWS_ACCOUNT_ID).Replace('${AWS_REGION}', $env:AWS_REGION).Replace('${IMAGE_TAG}', $Tag)
$Compose = Join-Path $Out "docker-compose.yml"
Set-Content -Path $Compose -Value $Rendered -Encoding UTF8
$Zip = Join-Path $Root "dist/campuspulse-eb-$Tag.zip"
if (Test-Path $Zip) { Remove-Item $Zip -Force }
Compress-Archive -Path $Compose -DestinationPath $Zip
Write-Output $Zip
