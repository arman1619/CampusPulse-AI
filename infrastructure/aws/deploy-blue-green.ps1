param(
  [Parameter(Mandatory=$true)][string]$Tag,
  [Parameter(Mandatory=$true)][string]$InactiveEnvironment
)
$ErrorActionPreference = "Stop"
foreach ($Name in @('AWS_REGION','EB_ARTIFACT_BUCKET')) { if (-not (Get-Item "Env:$Name" -ErrorAction SilentlyContinue)) { throw "$Name required" } }
$Root = Resolve-Path (Join-Path $PSScriptRoot "../..")
& (Join-Path $PSScriptRoot "package-eb.ps1") -Tag $Tag
$Zip = Join-Path $Root "dist/campuspulse-eb-$Tag.zip"
$Key = "releases/campuspulse-eb-$Tag.zip"
aws s3 cp $Zip "s3://$($env:EB_ARTIFACT_BUCKET)/$Key" --region $env:AWS_REGION
$App = if ($env:EB_APPLICATION_NAME) { $env:EB_APPLICATION_NAME } else { 'campuspulse-ai' }
aws elasticbeanstalk create-application-version --application-name $App --version-label $Tag --source-bundle "S3Bucket=$($env:EB_ARTIFACT_BUCKET),S3Key=$Key" --region $env:AWS_REGION
aws elasticbeanstalk update-environment --environment-name $InactiveEnvironment --version-label $Tag --region $env:AWS_REGION
aws elasticbeanstalk wait environment-updated --environment-name $InactiveEnvironment --region $env:AWS_REGION
