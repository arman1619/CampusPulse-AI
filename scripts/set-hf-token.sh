#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
[ -f "$ENV_FILE" ] || cp "$ROOT/.env.example" "$ENV_FILE"
read -r -s -p "Paste your Hugging Face token: " TOKEN; echo
[[ "$TOKEN" == hf_* ]] || { echo "Token must start with hf_" >&2; exit 1; }
python - "$ENV_FILE" "$TOKEN" <<'PY'
from pathlib import Path
import sys
path=Path(sys.argv[1]); token=sys.argv[2]
lines=path.read_text().splitlines(); out=[]; found=False
for line in lines:
    if line.startswith('HF_TOKEN='):
        out.append('HF_TOKEN='+token); found=True
    else: out.append(line)
if not found: out.append('HF_TOKEN='+token)
path.write_text('\n'.join(out)+'\n')
PY
chmod 600 "$ENV_FILE" 2>/dev/null || true
echo "HF_TOKEN saved to local .env (excluded from Git/release ZIP)."
