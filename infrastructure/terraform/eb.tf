data "aws_elastic_beanstalk_solution_stack" "docker" {
  most_recent = true
  name_regex  = "64bit Amazon Linux 2023.*running Docker"
}

resource "aws_s3_bucket" "artifacts" {
  bucket_prefix = "${var.project_name}-eb-artifacts-"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_elastic_beanstalk_application" "main" {
  name        = "${var.project_name}-ai"
  description = "CampusPulse AI container application"
}

locals {
  environments = var.enable_blue_green ? toset(["blue", "green"]) : toset(["blue"])
}

resource "aws_elastic_beanstalk_environment" "env" {
  for_each = local.environments

  name                = "${var.project_name}-${each.key}"
  application         = aws_elastic_beanstalk_application.main.name
  solution_stack_name = data.aws_elastic_beanstalk_solution_stack.docker.name
  tier                = "WebServer"

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = aws_iam_instance_profile.eb.name
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "InstanceType"
    value     = var.eb_instance_type
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "SecurityGroups"
    value     = aws_security_group.eb.id
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "DisableDefaultEC2SecurityGroup"
    value     = "true"
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "DisableIMDSv1"
    value     = "true"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "VPCId"
    value     = aws_vpc.main.id
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "Subnets"
    value     = join(",", [aws_subnet.public_a.id, aws_subnet.public_b.id])
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "ELBSubnets"
    value     = join(",", [aws_subnet.public_a.id, aws_subnet.public_b.id])
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "ELBScheme"
    value     = "public"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "AssociatePublicIpAddress"
    value     = "true"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "ServiceRole"
    value     = aws_iam_role.eb_service.arn
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "EnvironmentType"
    value     = "LoadBalanced"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "LoadBalancerType"
    value     = "application"
  }

  setting {
    namespace = "aws:elbv2:loadbalancer"
    name      = "SecurityGroups"
    value     = aws_security_group.alb.id
  }

  setting {
    namespace = "aws:elbv2:loadbalancer"
    name      = "ManagedSecurityGroup"
    value     = aws_security_group.alb.id
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "Port"
    value     = "8080"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "HealthCheckPath"
    value     = "/gateway-health"
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "MatcherHTTPCode"
    value     = "200"
  }

  setting {
    namespace = "aws:autoscaling:asg"
    name      = "MinSize"
    value     = "1"
  }

  setting {
    namespace = "aws:autoscaling:asg"
    name      = "MaxSize"
    value     = "2"
  }

  setting {
    namespace = "aws:elasticbeanstalk:healthreporting:system"
    name      = "SystemType"
    value     = "enhanced"
  }

  setting {
    namespace = "aws:elasticbeanstalk:cloudwatch:logs"
    name      = "StreamLogs"
    value     = "true"
  }

  setting {
    namespace = "aws:elasticbeanstalk:cloudwatch:logs"
    name      = "DeleteOnTerminate"
    value     = "false"
  }

  setting {
    namespace = "aws:elasticbeanstalk:cloudwatch:logs"
    name      = "RetentionInDays"
    value     = tostring(var.log_retention_days)
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ENVIRONMENT"
    value     = "production"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "LOG_LEVEL"
    value     = "INFO"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "JWT_ALGORITHM"
    value     = "HS256"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "JWT_EXPIRE_MINUTES"
    value     = "60"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "SEED_DEMO"
    value     = "false"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "CORS_ORIGINS"
    value     = "[]"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AI_SERVICE_URL"
    value     = "http://ai-service:8003"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "NOTIFICATION_SERVICE_URL"
    value     = "http://notification-service:8004"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AI_CONFIDENCE_THRESHOLD"
    value     = "0.75"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AI_MODEL_ID"
    value     = "meta-llama/Llama-3.1-8B-Instruct"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AI_PROVIDER"
    value     = "auto"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AI_BACKEND"
    value     = "huggingface"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AI_REQUIRE_LLM"
    value     = "true"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AI_API_TIMEOUT_SECONDS"
    value     = "45"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AI_MAX_RETRIES"
    value     = "2"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AI_MAX_TOKENS"
    value     = "180"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AI_TEMPERATURE"
    value     = "0.0"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ASSISTANT_MODEL_ID"
    value     = "meta-llama/Llama-3.1-8B-Instruct"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ASSISTANT_PROVIDER"
    value     = "auto"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ASSISTANT_BACKEND"
    value     = "huggingface"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ASSISTANT_REQUIRE_LLM"
    value     = "true"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ASSISTANT_API_TIMEOUT_SECONDS"
    value     = "45"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ASSISTANT_MAX_RETRIES"
    value     = "2"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ASSISTANT_MAX_NEW_TOKENS"
    value     = "220"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ASSISTANT_TEMPERATURE"
    value     = "0.2"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "ASSISTANT_TOP_P"
    value     = "0.9"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environmentsecrets"
    name      = "JWT_SECRET"
    value     = "${aws_secretsmanager_secret.app.arn}:JWT_SECRET"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environmentsecrets"
    name      = "INTERNAL_SERVICE_TOKEN"
    value     = "${aws_secretsmanager_secret.app.arn}:INTERNAL_SERVICE_TOKEN"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environmentsecrets"
    name      = "POSTGRES_ADMIN_URL"
    value     = "${aws_secretsmanager_secret.app.arn}:POSTGRES_ADMIN_URL"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environmentsecrets"
    name      = "AUTH_DATABASE_URL"
    value     = "${aws_secretsmanager_secret.app.arn}:AUTH_DATABASE_URL"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environmentsecrets"
    name      = "FEEDBACK_DATABASE_URL"
    value     = "${aws_secretsmanager_secret.app.arn}:FEEDBACK_DATABASE_URL"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environmentsecrets"
    name      = "NOTIFICATION_DATABASE_URL"
    value     = "${aws_secretsmanager_secret.app.arn}:NOTIFICATION_DATABASE_URL"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environmentsecrets"
    name      = "ASSISTANT_DATABASE_URL"
    value     = "${aws_secretsmanager_secret.app.arn}:ASSISTANT_DATABASE_URL"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environmentsecrets"
    name      = "HF_TOKEN"
    value     = "${aws_secretsmanager_secret.app.arn}:HF_TOKEN"
  }

  depends_on = [
    aws_secretsmanager_secret_version.app,
    aws_iam_role_policy.eb_secrets
  ]
}
