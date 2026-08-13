resource "aws_codecommit_repository" "main" {
  count = var.enable_codecommit ? 1 : 0

  repository_name = "${var.project_name}-ai"
  description     = "AWS mirror of the CampusPulse AI Git repository for SWE7303 demonstration"
}

data "aws_iam_policy_document" "codebuild_assume" {
  count = var.enable_codebuild && var.enable_codecommit ? 1 : 0

  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "codebuild" {
  count = var.enable_codebuild && var.enable_codecommit ? 1 : 0

  name               = "${var.project_name}-codebuild"
  assume_role_policy = data.aws_iam_policy_document.codebuild_assume[0].json
}

resource "aws_iam_role_policy" "codebuild" {
  count = var.enable_codebuild && var.enable_codecommit ? 1 : 0

  name = "${var.project_name}-codebuild-ci"
  role = aws_iam_role.codebuild[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["ecr:GetAuthorizationToken"]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ]
        Resource = [for r in aws_ecr_repository.services : r.arn]
      },
      {
        Effect   = "Allow"
        Action   = ["codecommit:GitPull"]
        Resource = var.enable_codecommit ? [aws_codecommit_repository.main[0].arn] : ["*"]
      }
    ]
  })
}

resource "aws_codebuild_project" "verification" {
  count = var.enable_codebuild && var.enable_codecommit ? 1 : 0

  name           = "${var.project_name}-verification"
  description    = "Independent AWS CI verification path; Jenkins remains the primary release orchestrator"
  service_role   = aws_iam_role.codebuild[0].arn
  build_timeout  = 45
  queued_timeout = 30

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = var.codebuild_compute_type
    image                       = var.codebuild_image
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

    environment_variable {
      name  = "AWS_REGION"
      value = var.aws_region
    }

    environment_variable {
      name  = "PROJECT_NAME"
      value = var.project_name
    }
  }

  source {
    type            = "CODECOMMIT"
    location        = aws_codecommit_repository.main[0].clone_url_http
    buildspec       = "buildspec.yml"
    git_clone_depth = 1
  }

  logs_config {
    cloudwatch_logs {
      group_name  = "/aws/codebuild/${var.project_name}-verification"
      stream_name = "build"
    }
  }
}
