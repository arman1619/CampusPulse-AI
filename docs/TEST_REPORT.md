# CampusPulse AI Test Report — Hosted Llama Release

**Verification date:** 12 August 2026

This report records only checks executed against this release in the available build environment. Hosted Hugging Face calls, Docker runtime and AWS deployment are explicitly separated where external access was unavailable.

## Automated service tests

| Service | Result | Observed coverage |
|---|---:|---:|
| Auth | 3 passed | 79% overall |
| Feedback | 5 passed | 89% |
| Hosted-Llama triage AI | 10 passed | 81% |
| Notifications | 2 passed | 92% |
| Hosted-Llama assistant | 10 passed | 85% |
| **Total** | **30 passed, 0 failed** | — |

The AI and assistant unit suites do not consume Hugging Face credit. They use deterministic CI backends or mocked `InferenceClient` responses to validate API contracts, schema parsing, RBAC/guardrails, retrieval and failure behavior. Production defaults remain hosted Hugging Face inference.

## AI triage control evaluation

`PYTHONPATH=services/ai-service python services/ai-service/evaluation/evaluate.py` was executed.

- deterministic critical-safety hazard recall: **1.0000** on the bundled control set;
- safety-rule false-positive rate: **0.0000** on the bundled non-hazard set;
- hosted-response JSON/schema parser pass rate: **1.0000** on the bundled parser cases;
- local AI model weights: **false**.

These are control/integration metrics, **not predictive-accuracy claims for Llama 3.1**. Live Llama quality is provider/model dependent and requires token-backed manual/smoke evidence.

## Assistant evaluation

`PYTHONPATH=services/assistant-service python services/assistant-service/evaluation/evaluate.py` was executed.

- retrieval Hit@3: **1.0000**;
- retrieval MRR@3: **0.9375**;
- immediate-hazard guardrail recall: **1.0000**;
- prompt-injection block rate: **1.0000**.

The test corpus is small and authored for demonstration. These figures do not establish universal chatbot safety or factuality.

## Cross-service integration

`python tests/integration/test_contracts.py` passed. `python tests/integration/run_local_flow.py` also passed using isolated SQLite integration databases and quota-free deterministic CI backends:

`login → JWT → feedback persistence → AI triage contract → safety escalation → notification → staff assignment → status transition → human override → admin analytics → assistant grounding/guardrail`.

The exposed-electrical-wiring scenario was preserved as `CRITICAL / SAFETY_RULE`; ordinary Library Wi-Fi remained non-critical.

## Static/release validation

Executed successfully:

- Python byte-code compilation across services/scripts/tests;
- YAML/JSON parsing for Compose/buildspec/generated files;
- Bash syntax checking for project/AWS scripts;
- TypeScript/TSX syntax parsing across **33** frontend source/test/config files;
- release structure and secret-pattern scanning;
- explicit scan for Hugging Face user-access-token patterns;
- ZIP exclusion rules for `.env`, credentials, private keys, local DBs, caches, virtual environments and model weights.

The previous TypeScript `TS5096` configuration problem is corrected by setting `noEmit: true` in `frontend/tsconfig.node.json`. A full dependency-based frontend build was not executed in this sandbox because `node_modules` was not installed here.

## Not executed in this build environment

- real Hugging Face Llama inference: network/token/provider access was unavailable to the build sandbox;
- frontend Vitest/ESLint/full Vite production build: dependencies were not installed in this sandbox;
- Docker image build and Compose runtime: Docker daemon unavailable to this build sandbox;
- Ruff/Bandit/pip-audit/Trivy execution: not all CLIs were available locally (they remain CI stages);
- `terraform fmt/validate/plan`: Terraform CLI unavailable;
- AWS provisioning/deployment: no AWS credentials/account were available.

A real hosted-Llama check is provided through `tests/smoke/hf_llama_smoke.py` and `tests/smoke/hf_llama_triage_smoke.py`. Run these only with a valid masked `HF_TOKEN`, accepted model access, Internet connectivity and available Inference Providers credit/quota.

## Required student-machine verification

Before claiming the application/AWS deployment as demonstrated, capture real evidence for: frontend build/tests, seven Docker image builds, Compose healthy/readiness, both hosted-Llama smoke tests, security gates, Terraform validation/plan, ECR push, RDS, inactive Elastic Beanstalk smoke, blue-green CNAME promotion, CloudWatch monitoring and rollback. Follow `docs/EVIDENCE_CHECKLIST.md`.
