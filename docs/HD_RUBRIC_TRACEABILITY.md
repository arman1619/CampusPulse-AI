# SWE7303 HE7 / 85–100% Engineering Traceability

This document is an engineering evidence map, not a guarantee of a mark. The final mark also depends on the submitted report, the group's genuine practical evidence, the student's own reflection, referencing and assessor judgement.

## Assessment weighting alignment
| Brief area | Weight | Project evidence |
|---|---:|---|
| DevOps Architecture — knowledge, pipeline, deployment, project | 50% | `docs/ARCHITECTURE.md`, root `Jenkinsfile`, `buildspec.yml`, Docker/Compose, Terraform, AWS scripts, blue-green/rollback, seven ECR images, private RDS, Secrets Manager, observability |
| Personal Reflection & Role | 20% | `docs/PERSONAL_REFLECTION_FRAMEWORK.md` only; student/group must supply truthful first-person evidence |
| Report formatting & References | 10% | `docs/RESEARCH_SOURCE_PLAN.md`, diagram sources, evidence naming; final academic report remains a separate deliverable |
| Practical Demonstrations | 20% | `docs/DEMO_SCRIPT.md`, `docs/EVIDENCE_CHECKLIST.md`, smoke/integration/security/failure demonstrations |

## LO1 — Plan, construct and implement
Evidence includes independently containerised frontend/gateway/auth/feedback/classification-AI/notification/LLM-assistant components; CRUD and persistent PostgreSQL data; automated tests; schema-validated hosted triage plus deterministic safety controls; hosted Llama inference through a secret-managed Hugging Face API client; CI/CD and deploy/rollback scripts.

## LO2 — Critically evaluate implementation strategies
Trade-offs are explicitly documented rather than claiming a universal best choice: synchronous HTTP vs broker, single RDS instance with logical databases vs per-service instances, Beanstalk vs ECS/EKS, Compose vs Kubernetes, Jenkins vs managed AWS CI/CD, hosted inference vs local model hosting, TF-IDF retrieval vs vector database, blue-green vs rolling deployment.

## LO3 — Critically evaluate tools
`docs/DEVOPS_PIPELINE.md`, `docs/LLM_ASSISTANT.md`, `docs/SECURITY.md` and `docs/DEPLOYMENT.md` explain why each selected tool fits the assessed constraints and where its limitations appear.

## Requirements from the task
- **Git:** repository-ready structure, SHA image tagging and GitHub/CodeCommit workflow documentation.
- **Jenkins:** root Pipeline as Code with quality/test/security/build/deploy gates.
- **Docker:** production Dockerfiles and Compose for multiple microservices.
- **AWS CodeCommit:** Terraform-provisioned optional AWS mirror repository.
- **AWS CodeBuild:** Terraform-provisioned independent verification project using root `buildspec.yml`.
- **Elastic Beanstalk:** multi-container Compose package, inactive-environment deployment and CNAME promotion.
- **Multiple microservices:** auth, feedback, AI classification, notifications and LLM assistant are independently deployable services.
- **Automated testing:** service tests, deterministic AI/assistant evaluations, frontend tests and live integration/smoke flows.
- **Minimal downtime:** blue-green deployment with pre-switch health/smoke gate.
- **Monitoring/logging:** structured logs, correlation IDs, Prometheus/Grafana locally, EB log streaming/CloudWatch alarms in AWS.
- **Rollback:** retained prior environment + explicit CNAME reversal script and local rollback simulation.
- **Documentation/maintainability:** API/database/model/security/deployment/monitoring/demo/evidence documents and reproducible diagram sources.

## Evidence that cannot be manufactured by source code
The following must be produced by the group during its own deployment/demonstration: GitHub link/commit history, Jenkins run screenshots, AWS ECR/RDS/Beanstalk/CloudWatch screenshots, actual live URL, blue-green CNAME swap, rollback evidence, team work division, meeting/role evidence and each student's genuine personal reflection.
