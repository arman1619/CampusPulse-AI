# AWS Deployment and Demonstration Checklist

This checklist separates configuration readiness from evidence that must be created in the student's AWS account.

## Before provisioning
- [ ] Configure AWS CLI using a dedicated IAM principal/role; do not place credentials in `.env` or Terraform files.
- [ ] Confirm region and expected cost for RDS, two Beanstalk environments, EC2/ALB, ECR, S3, Secrets Manager, CloudWatch/SNS and CodeBuild.
- [ ] Create/secure Terraform remote state if the group will share infrastructure state.
- [ ] Set a reviewed immutable Hugging Face model revision for the final deployment.

## Terraform
- [ ] `terraform init`
- [ ] `terraform fmt -check`
- [ ] `terraform validate`
- [ ] review `terraform plan`
- [ ] `terraform apply`
- [ ] record seven ECR repositories
- [ ] record private RDS state/security groups
- [ ] record Secrets Manager resource without displaying secret values
- [ ] record blue and green Beanstalk environments
- [ ] record CodeCommit and CodeBuild resources if enabled
- [ ] confirm CloudWatch/SNS baseline alarms

## Source and CI
- [ ] Push source to GitHub and record commit SHA.
- [ ] Mirror the commit to CodeCommit when demonstrating the AWS-native path.
- [ ] Run Jenkins through tests, security, Docker build and local smoke.
- [ ] Run CodeBuild verification and capture result.
- [ ] Confirm intentionally broken test prevents downstream deployment, then restore code.

## Container release
- [ ] Confirm all seven application images exist locally.
- [ ] Trivy scan the seven images.
- [ ] Push the same immutable SHA tag to all ECR repositories.
- [ ] Confirm assistant image contains the model and does not require Internet at runtime.

## Inactive deployment
- [ ] Package the ECR-backed Beanstalk Compose version.
- [ ] Deploy to the inactive environment only.
- [ ] Verify `/gateway-health` and every backend health endpoint.
- [ ] Verify `/api/assistant/ready` reports model ready.
- [ ] Run full smoke test against the candidate URL.
- [ ] Test student feedback → AI → notification.
- [ ] Test LLM grounded answer, prompt-injection refusal and safety response.

## Promotion
- [ ] Record current BLUE/GREEN roles.
- [ ] Obtain group promotion approval.
- [ ] Swap CNAMEs/traffic.
- [ ] Run production smoke test immediately.
- [ ] Confirm logs/health/metrics in CloudWatch.
- [ ] Retain previous healthy environment for rollback window.

## Rollback demonstration
- [ ] Demonstrate a failed candidate that never receives traffic **or** an approved controlled reversal.
- [ ] Execute documented CNAME swap-back where safe.
- [ ] Re-run smoke test on restored active version.
- [ ] Record version/environment evidence without fabricating an outage.

## Final traceability
- [ ] Same Git SHA visible in GitHub/Jenkins/ECR/Beanstalk application version.
- [ ] RDS data survives application environment deployment.
- [ ] CloudWatch evidence corresponds to the deployed environment/time.
- [ ] Remove/terminate unused cloud resources after assessment if required by cost policy.
