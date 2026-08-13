pipeline {
  agent any
  options {
    timestamps()
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '20'))
    timeout(time: 120, unit: 'MINUTES')
  }
  parameters {
    booleanParam(name: 'RUN_HOSTED_LLM_SMOKE', defaultValue: false, description: 'Run one real Hugging Face Llama API smoke request using Jenkins credential campuspulse-hf-token')
  }
  environment {
    PYTHONUNBUFFERED = '1'
    RELEASE_SHA = "${env.GIT_COMMIT ?: 'local'}"
    DOCKER_BUILDKIT = '1'
  }
  stages {
    stage('Checkout') {
      steps { checkout scm; sh 'git rev-parse --short HEAD || true' }
    }
    stage('Environment validation') {
      steps {
        sh 'python --version && node --version && npm --version && docker --version && docker compose version'
        sh 'python scripts/release_check.py'
        sh 'docker compose config -q'
      }
    }
    stage('Install CI dependencies') {
      steps {
        sh 'python -m pip install --upgrade pip'
        sh 'python -m pip install ruff pytest pytest-cov bandit pip-audit'
        sh 'for s in auth-service feedback-service ai-service notification-service; do python -m pip install -r services/$s/requirements.txt; done'
        sh 'python -m pip install -r services/assistant-service/requirements-ci.txt'
        dir('frontend') { sh 'npm install --no-audit --no-fund' }
      }
    }
    stage('Python lint') {
      steps { sh 'for s in auth-service feedback-service ai-service notification-service assistant-service; do (cd services/$s && ruff check app tests); done' }
    }
    stage('Frontend lint') {
      steps { dir('frontend') { sh 'npm run lint' } }
    }
    stage('Backend and assistant unit tests') {
      steps {
        sh '''for s in auth-service feedback-service notification-service assistant-service; do
          (cd services/$s && PYTHONPATH=. pytest --junitxml=../../test-$s.xml --cov=app --cov-report=xml:../../coverage-$s.xml)
        done'''
      }
    }
    stage('AI and LLM evaluation') {
      steps {
        dir('services/ai-service') {
          sh 'PYTHONPATH=. python evaluation/evaluate.py'
          sh 'PYTHONPATH=. pytest --junitxml=../../test-ai.xml --cov=app --cov-report=xml:../../coverage-ai.xml'
        }
        dir('services/assistant-service') { sh 'PYTHONPATH=. python evaluation/evaluate.py' }
      }
    }
    stage('Frontend tests and production build') {
      steps { dir('frontend') { sh 'npm test'; sh 'npm run build' } }
    }
    stage('Integration contracts') {
      steps { sh 'python tests/integration/test_contracts.py' }
    }
    stage('Dependency and source security gates') {
      steps {
        sh '''for s in auth-service feedback-service ai-service notification-service assistant-service; do
          (cd services/$s && bandit -q -r app && pip-audit -r requirements.txt --progress-spinner=off)
        done'''
        dir('frontend') { sh 'npm audit --audit-level=high' }
      }
    }
    stage('Docker build') {
      steps { sh 'docker compose build --pull' }
    }
    stage('Container vulnerability scan') {
      steps {
        sh '''for image in campuspulse-ai-auth-service campuspulse-ai-feedback-service campuspulse-ai-ai-service campuspulse-ai-notification-service campuspulse-ai-assistant-service campuspulse-ai-frontend campuspulse-ai-gateway; do
          trivy image --exit-code 1 --severity CRITICAL --ignore-unfixed "$image:latest"
        done'''
      }
    }
    stage('Local compose smoke test') {
      steps {
        sh 'ASSISTANT_BACKEND=template ASSISTANT_REQUIRE_LLM=false docker compose up -d'
        sh 'python scripts/wait_for_stack.py --url http://localhost:8080 --timeout 360'
        sh 'python tests/smoke/smoke.py --base-url http://localhost:8080'
      }
      post { always { sh 'docker compose down -v || true' } }
    }
    stage('Hosted Llama API smoke (opt-in)') {
      when { expression { return params.RUN_HOSTED_LLM_SMOKE } }
      steps {
        withCredentials([string(credentialsId: 'campuspulse-hf-token', variable: 'HF_TOKEN')]) {
          sh 'PYTHONPATH=services/assistant-service python tests/smoke/hf_llama_smoke.py'
          sh 'PYTHONPATH=services/ai-service python tests/smoke/hf_llama_triage_smoke.py'
        }
      }
    }
    stage('Tag images') { steps { sh 'scripts/tag-images.sh "$RELEASE_SHA"' } }
    stage('Push immutable images to ECR') {
      when { allOf { expression { env.AWS_ACCOUNT_ID?.trim() }; expression { env.AWS_REGION?.trim() } } }
      steps { sh 'infrastructure/aws/push-ecr.sh "$RELEASE_SHA"' }
    }
    stage('Optional AWS CodeBuild verification') {
      when { allOf { expression { env.CODEBUILD_PROJECT_NAME?.trim() }; expression { env.AWS_REGION?.trim() } } }
      steps { sh 'infrastructure/aws/run-codebuild-verification.sh "$CODEBUILD_PROJECT_NAME"' }
    }
    stage('Package Elastic Beanstalk release') {
      when { expression { env.AWS_ACCOUNT_ID?.trim() } }
      steps { sh 'infrastructure/aws/package-eb.sh "$RELEASE_SHA"' }
    }
    stage('Deploy to inactive blue/green environment') {
      when { allOf { expression { env.AWS_ACCOUNT_ID?.trim() }; expression { env.EB_INACTIVE_ENV?.trim() }; expression { env.EB_ARTIFACT_BUCKET?.trim() } } }
      steps { sh 'infrastructure/aws/deploy-blue-green.sh "$RELEASE_SHA" "$EB_INACTIVE_ENV"' }
    }
    stage('Inactive environment smoke and readiness') {
      when { expression { env.EB_INACTIVE_URL?.trim() } }
      steps {
        sh 'python scripts/wait_for_stack.py --url "$EB_INACTIVE_URL" --timeout 360'
        sh 'python tests/smoke/smoke.py --base-url "$EB_INACTIVE_URL"'
      }
    }
    stage('Blue-green traffic switch') {
      when { allOf { expression { env.EB_ACTIVE_ENV?.trim() }; expression { env.EB_INACTIVE_ENV?.trim() }; expression { env.AWS_REGION?.trim() } } }
      steps {
        input message: 'Promote the verified inactive environment to production?', ok: 'Swap traffic'
        sh 'aws elasticbeanstalk swap-environment-cnames --region "$AWS_REGION" --source-environment-name "$EB_ACTIVE_ENV" --destination-environment-name "$EB_INACTIVE_ENV"'
      }
    }
    stage('Production smoke test') {
      when { expression { env.PRODUCTION_URL?.trim() } }
      steps { sh 'python tests/smoke/smoke.py --base-url "$PRODUCTION_URL"' }
    }
    stage('Release manifest') { steps { sh 'python scripts/write_release_manifest.py' } }
  }
  post {
    always {
      junit allowEmptyResults: true, testResults: 'test-*.xml'
      archiveArtifacts allowEmptyArchive: true, artifacts: 'coverage-*.xml,docs/generated/**,dist/**'
      cleanWs deleteDirs: true, notFailBuild: true
    }
  }
}
