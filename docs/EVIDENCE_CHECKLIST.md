# Practical Evidence Checklist

Use real screenshots only. Preserve Git SHA/environment name/time where practical so evidence is traceable.

| # | Suggested filename | What must be visible | Why / criterion |
|---:|---|---|---|
| 01 | `01-github-repository.png` | GitHub tree + commit SHA | Git/source control and maintainability |
| 02 | `02-login.png` | working login | user interaction/auth |
| 03 | `03-student-dashboard.png` | real counts/recent issues | functioning application |
| 04 | `04-submit-feedback.png` | issue form and successful submission | CRUD |
| 05 | `05-ai-triage.png` | category/sentiment/priority/confidences | AI integration |
| 06 | `06-safety-rule.png` | electrical-wiring case = CRITICAL / SAFETY_RULE | responsible AI/risk control |
| 07 | `07-staff-dashboard.png` | filters/review queue | role workflow |
| 08 | `08-human-override.png` | original AI + override reason/final decision | human oversight/audit |
| 09 | `09-admin-analytics.png` | DB-derived charts | analytics |
| 10 | `10-notifications.png` | unread/read state | microservice feature |
| 11 | `11-llm-assistant.png` | Llama 3.1 chat answer + source cards + hosted provider/model info | original AI/LLM feature |
| 12 | `12-llm-model-info.png` | model ID, local backend, offline/grounding metadata | model traceability |
| 13 | `13-llm-guardrail.png` | prompt-injection refusal or immediate-hazard deterministic response | LLM security/responsible AI |
| 14 | `14-hf-llama-ready.png` | assistant `/ready` + `/model-info` showing hosted API configuration; token value must remain hidden | secure external LLM integration / no local weight storage |
| 15 | `15-pytest.png` | backend/AI/assistant passing tests | automated testing |
| 16 | `16-frontend-tests.png` | Vitest + frontend build | frontend quality |
| 17 | `17-ai-evaluation.png` | hosted-triage safety/schema evaluation + model-info | AI evaluation |
| 18 | `18-assistant-evaluation.png` | retrieval/guardrail JSON metrics | assistant evaluation |
| 19 | `19-docker-images.png` | seven application images | containerisation/microservices |
| 20 | `20-compose-healthy.png` | `docker compose ps` healthy services | integrated local deployment |
| 21 | `21-smoke-test.png` | gateway + all service health/readiness passes | deployment verification |
| 22 | `22-jenkins-success.png` | full green pipeline + SHA | Jenkins CI/CD |
| 23 | `23-jenkins-failure-gate.png` | intentional test failure and skipped deployment | pipeline protection |
| 24 | `24-security-scans.png` | Bandit/audit/Trivy result | DevSecOps |
| 25 | `25-codecommit.png` | AWS mirror repo/commit | named AWS source-control service |
| 26 | `26-codebuild.png` | CodeBuild verification success | named AWS build service |
| 27 | `27-ecr.png` | seven repositories + immutable SHA tag | artifact registry/traceability |
| 28 | `28-rds.png` | private RDS status/endpoint (mask sensitive details) | persistent AWS data |
| 29 | `29-secrets-manager.png` | secret resource names only, never values | secure configuration |
| 30 | `30-eb-blue-green.png` | blue and green environments/health | minimal-downtime architecture |
| 31 | `31-live-aws-app.png` | public live app + EB URL | practical deployment |
| 32 | `32-cloudwatch-logs.png` | current application/deployment logs | monitoring/logging |
| 33 | `33-cloudwatch-health-alarm.png` | enhanced health/alarm state | early detection |
| 34 | `34-blue-green-swap.png` | candidate verified + CNAME swap evidence | minimal downtime |
| 35 | `35-rollback.png` | failed candidate or controlled CNAME reversal | rollback |
| 36 | `36-git-pipeline-trace.png` | same SHA in Git/Jenkins/ECR/EB | end-to-end traceability |
| 37 | `37-grafana.png` | real service/assistant request panels | observability |
| 38 | `38-audit-view.png` | status/override/admin audit events | accountability |

For the 20% practical-demonstration area, prioritise a coherent story rather than unrelated screenshots: commit → tests/security → images → candidate deployment → verification → promotion → monitoring → rollback readiness.
