provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "CampusPulse-AI"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
