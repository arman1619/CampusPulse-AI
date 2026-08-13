locals {
  ecr_repositories = toset([
    "campuspulse-frontend",
    "campuspulse-gateway",
    "campuspulse-auth",
    "campuspulse-feedback",
    "campuspulse-ai",
    "campuspulse-notification",
    "campuspulse-assistant"
  ])
}

resource "aws_ecr_repository" "services" {
  for_each = local.ecr_repositories

  name                 = each.value
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

resource "aws_ecr_lifecycle_policy" "services" {
  for_each = aws_ecr_repository.services

  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Retain 30 most recent images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 30
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
