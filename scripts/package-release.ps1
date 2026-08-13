$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
python scripts/release_check.py
python scripts/write_release_manifest.py
python scripts/package_release.py
