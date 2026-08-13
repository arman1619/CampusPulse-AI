$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$EnvFile = Join-Path $Root ".env"
if (-not (Test-Path $EnvFile)) { Copy-Item (Join-Path $Root ".env.example") $EnvFile }
$Secure = Read-Host "Paste your Hugging Face token" -AsSecureString
$Ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secure)
try { $Token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Ptr) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Ptr) }
if (-not $Token.StartsWith("hf_")) { throw "Token must start with hf_" }
$Lines = Get-Content $EnvFile
$Found = $false
$Updated = foreach ($Line in $Lines) {
  if ($Line -match '^HF_TOKEN=') { $Found = $true; "HF_TOKEN=$Token" } else { $Line }
}
if (-not $Found) { $Updated += "HF_TOKEN=$Token" }
Set-Content -Path $EnvFile -Value $Updated -Encoding UTF8
Write-Host "HF_TOKEN saved to local .env (excluded from Git/release ZIP)."
