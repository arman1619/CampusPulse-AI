# SWE7303 Assessment Mapping

The project implements the required cloud-native microservices scenario and DevOps pipeline while adding reproducible AI triage and a hosted Hugging Face Llama assistant as distinctive engineering scope.

## DevOps architecture / pipeline / deployment / project
Evidence: `docs/ARCHITECTURE.md`, root `Jenkinsfile`, `buildspec.yml`, all Dockerfiles, Compose files, `infrastructure/terraform/`, `infrastructure/aws/`, private RDS + Secrets Manager design, ECR immutable images, Elastic Beanstalk blue/green and rollback, Prometheus/Grafana/CloudWatch. This addresses the highest-weighted technical area.

## Multiple microservices
Independently containerised data/domain services: auth, feedback, classification AI, notifications and LLM assistant; frontend and gateway are separately built containers. Each backend exposes health/readiness/metrics where appropriate.

## Automated testing and practical test report
Service tests validate auth/RBAC/workflow/AI/safety/notifications/assistant isolation/guardrails/retrieval. Frontend tests are defined under `frontend/tests`. Integration contracts and live flows are under `tests/integration`; `tests/smoke` checks deployment health/readiness. `docs/TEST_REPORT.md` records only actually executed results.

## Minimal downtime and rollback
Blue/green environments permit candidate verification without disturbing the active environment. CNAME swap is gated; previous environment remains available for explicit reversal. Scripts and local simulation demonstrate the control path.

## Monitoring/logging
Correlation IDs, structured service logs, Prometheus metrics, Grafana provisioning, EB enhanced health/log streaming and CloudWatch/SNS baseline alarms support detection and diagnosis.

## Critical evaluation / HE7 depth
`docs/ARCHITECTURE.md`, `docs/DEVOPS_PIPELINE.md`, `docs/LLM_ASSISTANT.md`, `docs/SECURITY.md` and `docs/DEPLOYMENT.md` document trade-offs instead of merely listing technologies. `docs/HD_RUBRIC_TRACEABILITY.md` maps source artefacts to the brief.

## Personal reflection / role
The repository provides `docs/PERSONAL_REFLECTION_FRAMEWORK.md` but intentionally does not invent individual contribution. Each group member must write their own evidence-based reflection and role because that criterion assesses personal responsibility/self-awareness.

## Report formatting and references
The final report is a separate academic submission. `docs/RESEARCH_SOURCE_PLAN.md` captures the brief's HE7 research minimum and research areas. Students must verify/cite the required academic sources and follow the specified University referencing style; source code cannot substitute for this criterion.
