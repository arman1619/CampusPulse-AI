import argparse
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--base-url", default="http://localhost:8080")
args = parser.parse_args()
base = args.base_url.rstrip("/")
checks = [
    "/gateway-health",
    "/api/auth/health",
    "/api/feedback/health",
    "/api/ai/health",
    "/api/notifications/health",
    "/api/assistant/health",
    "/api/assistant/ready",
]
for path in checks:
    try:
        with urllib.request.urlopen(base + path, timeout=20) as response:
            if response.status >= 300:
                raise RuntimeError(f"{path}: HTTP {response.status}")
            print(f"PASS {path} HTTP {response.status}")
    except Exception as exc:
        raise SystemExit(f"FAIL {path}: {exc}") from exc
print("CampusPulse smoke health/readiness suite passed, including assistant readiness.")
