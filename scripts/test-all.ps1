$ErrorActionPreference="Stop"
$Root=(Resolve-Path (Join-Path $PSScriptRoot ".."))
foreach($service in @("auth-service","feedback-service","ai-service","notification-service","assistant-service")){Write-Host "== $service ==";Push-Location (Join-Path $Root "services/$service");$env:PYTHONPATH=".";pytest --cov=app --cov-report=term-missing;Pop-Location}
if(Test-Path (Join-Path $Root "frontend/node_modules")){Push-Location (Join-Path $Root "frontend");npm test;Pop-Location}else{Write-Warning "Frontend dependencies not installed; run npm ci in frontend before frontend tests."}
