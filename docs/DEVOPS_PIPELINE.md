# DevOps Pipeline Design

## Primary Jenkins pipeline
The root `Jenkinsfile` implements a gated release chain: checkout → environment validation → Python/frontend lint → backend tests → AI/assistant evaluations → frontend tests/build → integration contracts → dependency/static security → Docker build → Trivy → local Compose smoke → immutable image tag → ECR push → optional CodeBuild verification → Elastic Beanstalk package → inactive deployment → candidate smoke → manual promotion → CNAME swap → production smoke → archive evidence.

Cloud stages run only when the required AWS configuration exists. This separation allows repeatable CI before cloud credentials are introduced and prevents an AWS account from becoming a prerequisite for source-level testing.

## AWS CodeCommit and CodeBuild
Terraform can create an AWS CodeCommit mirror and a CodeBuild project. `buildspec.yml` performs an independent AWS verification path. Jenkins remains authoritative for release orchestration; CodeBuild demonstrates an AWS-managed build option and provides a useful cross-check rather than duplicating all deployment ownership.

## Deployment gating
A lint, unit, AI, assistant, frontend, security or container-build failure stops promotion. The demo script contains a reversible intentionally-failing assertion to prove downstream deployment is not executed. The repository is restored to green after the demonstration.

## Immutable traceability
Images are tagged with Git/release SHA and ECR repositories are immutable. Elastic Beanstalk versions reference that image tag, linking source → test run → image → environment. `latest` is not the deployment identity.

## Security gates
Ruff/ESLint address code quality; Bandit covers Python security lint; `pip-audit`/`npm audit` cover dependency advisories; Trivy scans built images. Critical findings are intended to block deployment. Security tooling cannot prove absence of vulnerability; results must be triaged rather than mechanically ignored.

## Tool critique
- **Jenkins:** excellent visibility, extensibility and Pipeline as Code; requires controller/plugin/credential maintenance.
- **CodeBuild:** removes build-server administration and integrates with IAM; more AWS-coupled and can make local reproduction less direct.
- **Docker:** immutable runtime units and consistent dependencies; image supply-chain and patch management remain operational responsibilities.
- **Elastic Beanstalk:** lower platform-management burden and explicit blue/green operations; less fine-grained orchestration than ECS/EKS.
- **Terraform:** reviewable infrastructure state/plan; provider/state governance and destructive-change discipline are required.
- **Prometheus/Grafana + CloudWatch:** rich local application metrics plus AWS-native operational visibility; duplicate telemetry stacks require clear ownership.

## Minimal downtime and rollback
The pipeline deploys to the inactive environment first. Health and smoke failures keep production traffic on the active environment. After CNAME swap, a production smoke failure triggers the documented rollback path. The previous healthy environment should not be terminated immediately after promotion.
