from __future__ import annotations
from datetime import datetime, timezone
import json, subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
dist = root / "dist"
dist.mkdir(exist_ok=True)
try:
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
except Exception:
    sha = "not-available-no-git-metadata"
assistant_metrics = root / "docs/generated/assistant_metrics.json"
ai_metrics_path = root / "docs/generated/ai_hosted_metrics.json"
metrics = json.loads(assistant_metrics.read_text()) if assistant_metrics.exists() else {}
ai = json.loads(ai_metrics_path.read_text()) if ai_metrics_path.exists() else {}
manifest = f"""CampusPulse AI HD+ LLM Release Manifest
========================================
Release timestamp (UTC): {datetime.now(timezone.utc).isoformat()}
Git SHA: {sha}
Services: frontend, gateway, auth, feedback, AI/NLP, notification, hosted-Llama assistant
Assistant model: meta-llama/Llama-3.1-8B-Instruct via Hugging Face Inference Providers; no LLM weights stored locally
Assistant retrieval hit@3: {metrics.get('retrieval_hit_at_3', 'not-run')}
Assistant guardrail hazard recall on bundled synthetic evaluation: {metrics.get('safety_hazard_recall', 'not-run')}
AI triage: meta-llama/Llama-3.1-8B-Instruct via Hugging Face Inference Providers; no local model weights
AI deterministic safety hazard recall: {ai.get('safety_hazard_recall', 'not-run')}
AI hosted-response schema parser pass rate: {ai.get('hosted_json_schema_parser_pass_rate', 'not-run')}
AWS: Terraform + ECR + private RDS + Secrets Manager + Elastic Beanstalk blue/green + CloudWatch + optional CodeCommit/CodeBuild
CI/CD: Jenkins primary pipeline; CodeBuild independent verification path
Known external verification dependencies: Docker daemon, npm registry, Terraform CLI, AWS credentials/account, Hugging Face token/model access/provider quota/network for hosted generation.
Security: no .env, Hugging Face tokens, AWS credentials, private keys, virtualenvs, node_modules, caches, local DBs, or LLM weights are packaged.
"""
(dist / "RELEASE_MANIFEST.txt").write_text(manifest)
print(dist / "RELEASE_MANIFEST.txt")
