resource "random_password" "db" {
  length  = 32
  special = false
}

resource "random_password" "jwt" {
  length  = 48
  special = false
}

resource "random_password" "internal" {
  length  = 48
  special = false
}

locals {
  db_password_effective = coalesce(var.db_password, random_password.db.result)
  db_base               = "postgresql+psycopg://${var.db_username}:${local.db_password_effective}@${aws_db_instance.postgres.address}:${aws_db_instance.postgres.port}"
}

resource "aws_secretsmanager_secret" "app" {
  name_prefix             = "${var.project_name}/${var.environment}/application-"
  description             = "CampusPulse application secrets and private RDS connection strings"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id

  lifecycle {
    precondition {
      condition     = var.hf_token != null ? startswith(var.hf_token, "hf_") : false
      error_message = "Set TF_VAR_hf_token to a valid Hugging Face token before AWS plan/apply for the hosted Llama assistant."
    }
  }

  secret_string = jsonencode({
    JWT_SECRET                = random_password.jwt.result
    INTERNAL_SERVICE_TOKEN    = random_password.internal.result
    POSTGRES_ADMIN_URL        = "${local.db_base}/postgres"
    AUTH_DATABASE_URL         = "${local.db_base}/campuspulse_auth"
    FEEDBACK_DATABASE_URL     = "${local.db_base}/campuspulse_feedback"
    NOTIFICATION_DATABASE_URL = "${local.db_base}/campuspulse_notifications"
    ASSISTANT_DATABASE_URL    = "${local.db_base}/campuspulse_assistant"
    HF_TOKEN                  = var.hf_token
  })
}
