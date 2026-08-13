locals {
  deployment_name = "${var.project_name}-${var.environment}"

  logical_databases = [
    "campuspulse_auth",
    "campuspulse_feedback",
    "campuspulse_notifications",
    "campuspulse_assistant"
  ]
}
