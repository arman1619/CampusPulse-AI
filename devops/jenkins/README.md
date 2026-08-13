# Local Jenkins demonstration

Start the optional academic Jenkins controller with:
```bash
docker compose -f devops/jenkins/docker-compose.jenkins.yml up -d
```
Configure a Pipeline job from the root `Jenkinsfile`. The Jenkins agent needs Git, Python 3.12+, Node/npm, Docker/Compose, and network access to dependency/model registries for a clean build. The pipeline itself installs Python/frontend test dependencies; the host also needs Trivy for the container security stage and AWS CLI for cloud stages.

The local academic Compose setup mounts the host Docker socket so Jenkins can build images. This effectively grants the Jenkins container privileged control over the Docker host and is **not** an enterprise reference pattern. A production CI design should prefer isolated/ephemeral agents or managed build capacity with least-privilege credentials.

AWS stages are conditional. Configure AWS credentials through Jenkins Credentials Binding/agent role, never in the repository. Supply `AWS_ACCOUNT_ID`, `AWS_REGION`, ECR/Beanstalk variables and optional `CODEBUILD_PROJECT_NAME`. The assistant image downloads the pinned Hugging Face model during Docker build, so the CI agent needs outbound model-registry access during that stage; the deployed container then runs offline.
