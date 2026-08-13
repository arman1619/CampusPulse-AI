from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
required = [
    "README.md", "Jenkinsfile", "buildspec.yml", "docker-compose.yml", "docker-compose.observability.yml",
    "frontend/package.json", "gateway/nginx.conf",
    "services/auth-service/migrations/versions/0001_initial.py",
    "services/feedback-service/migrations/versions/0001_initial.py",
    "services/notification-service/migrations/versions/0001_initial.py",
    "services/assistant-service/migrations/versions/0001_initial.py",
    "services/assistant-service/knowledge/campus_knowledge.json",
    "services/assistant-service/evaluation/assistant_eval_cases.json",
    "services/assistant-service/Dockerfile", "tests/smoke/hf_llama_smoke.py",
    "scripts/set-hf-token.ps1", "scripts/set-hf-token.sh",
    "services/ai-service/evaluation/evaluate.py", "tests/smoke/hf_llama_triage_smoke.py",
    "infrastructure/terraform/ecr.tf", "infrastructure/terraform/rds.tf", "infrastructure/terraform/eb.tf",
    "infrastructure/terraform/secrets.tf", "infrastructure/terraform/codebuild.tf",
    "infrastructure/aws/docker-compose.aws.yml.tpl", "infrastructure/aws/deploy-blue-green.sh",
    "docs/ARCHITECTURE.md", "docs/AI_MODEL_CARD.md", "docs/LLM_MODEL_CARD.md", "docs/LLM_ASSISTANT.md",
    "docs/TEST_REPORT.md", "docs/HD_RUBRIC_TRACEABILITY.md", "docs/EVIDENCE_CHECKLIST.md",
]
missing = [item for item in required if not (root / item).exists()]
if missing:
    raise SystemExit("Missing required release files: " + ", ".join(missing))

if (root / ".env").exists():
    print("NOTICE: local .env exists; packaging excludes it.")

patterns = {
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS secret assignment": re.compile(r"(?i)aws_secret_access_key\s*[=:]\s*['\"]?[A-Za-z0-9/+]{30,}"),
    "Hugging Face token": re.compile(r"hf_[A-Za-z0-9]{20,}"),
}
issues: list[str] = []
ignored_parts = {"node_modules", ".git", ".terraform", ".venv", "venv", "dist", "__pycache__"}
for path in root.rglob("*"):
    if not path.is_file() or any(part in ignored_parts for part in path.parts) or path.suffix in {".joblib", ".zip", ".pyc"}:
        continue
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        continue
    for label, pattern in patterns.items():
        if pattern.search(text):
            issues.append(f"{label}: {path.relative_to(root)}")
if issues:
    raise SystemExit("Potential release security issue(s): " + "; ".join(sorted(set(issues))))
print("Release structure, hosted-Llama/AWS artefacts and secret-pattern checks passed.")
