output "ecr_repository_urls" {
  value = { for k, v in aws_ecr_repository.services : k => v.repository_url }
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.address
}

output "rds_port" {
  value = aws_db_instance.postgres.port
}

output "elastic_beanstalk_application" {
  value = aws_elastic_beanstalk_application.main.name
}

output "elastic_beanstalk_environments" {
  value = { for k, v in aws_elastic_beanstalk_environment.env : k => v.name }
}

output "eb_artifact_bucket" {
  value = aws_s3_bucket.artifacts.bucket
}

output "application_secret_arn" {
  value     = aws_secretsmanager_secret.app.arn
  sensitive = true
}

output "codecommit_clone_url_http" {
  value = var.enable_codecommit ? aws_codecommit_repository.main[0].clone_url_http : null
}

output "codebuild_project_name" {
  value = var.enable_codebuild && var.enable_codecommit ? aws_codebuild_project.verification[0].name : null
}

output "alarm_topic_arn" {
  value = aws_sns_topic.alarms.arn
}
