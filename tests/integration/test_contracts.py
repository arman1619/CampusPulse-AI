from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
required = {
    "services/auth-service/app/main.py": ["/api/auth/register", "/api/auth/login", "/api/auth/me", "/api/auth/users"],
    "services/feedback-service/app/main.py": ["/api/feedback", "/status", "/comments", "/override", "/api/analytics/summary"],
    "services/ai-service/app/main.py": ["/api/ai/analyse", "/api/ai/model-info"],
    "services/notification-service/app/main.py": ["/api/notifications", "/unread-count", "/read-all"],
    "services/assistant-service/app/main.py": ["/api/assistant/chat", "/api/assistant/model-info", "/api/assistant/ready", "/api/assistant/sessions"],
}
for file, routes in required.items():
    text = (ROOT / file).read_text()
    for route in routes:
        assert route in text, f"{route} missing from {file}"
print("Cross-service API contract surface present, including hosted Llama assistant.")
