$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw "Docker Desktop / docker CLI is required." }
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
$HfLine = Get-Content .env | Where-Object { $_ -match '^HF_TOKEN=.+' } | Select-Object -First 1
$BackendLine = Get-Content .env | Where-Object { $_ -match '^ASSISTANT_BACKEND=' } | Select-Object -First 1
$Hosted = (-not $BackendLine) -or ($BackendLine -notmatch '=template$')
if ($Hosted -and -not $HfLine) { throw "HF_TOKEN is not configured. Run .\scripts\set-hf-token.ps1, then run dev-up.ps1 again." }
Write-Host "Starting CampusPulse AI..."
docker compose up --build -d
python scripts/wait_for_stack.py --url http://localhost:8080 --timeout 240
try { python scripts/seed_demo.py } catch { Write-Warning "Demo issue seeding skipped; demo users are still created by auth-service." }
Write-Host "CampusPulse AI: http://localhost:8080"
