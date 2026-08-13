variable "aws_region" {
  type    = string
  default = "eu-west-2"
}

variable "environment" {
  type    = string
  default = "demo"
}

variable "project_name" {
  type    = string
  default = "campuspulse"
}

variable "db_username" {
  type    = string
  default = "campuspulse"
}

variable "db_password" {
  type      = string
  sensitive = true
  default   = null
  nullable  = true

  validation {
    condition     = var.db_password == null || length(var.db_password) >= 16
    error_message = "db_password must be at least 16 characters when supplied. Omit it to let Terraform generate one."
  }
}

variable "hf_token" {
  type      = string
  sensitive = true
  default   = null
  nullable  = true

  validation {
    condition     = var.hf_token == null ? true : startswith(var.hf_token, "hf_")
    error_message = "hf_token must be a Hugging Face user access token beginning with hf_."
  }
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "db_allocated_storage" {
  type    = number
  default = 20
}

variable "db_multi_az" {
  type    = bool
  default = false
}

variable "rds_deletion_protection" {
  type    = bool
  default = false
}

variable "eb_instance_type" {
  type    = string
  default = "t3.small"
}

variable "enable_blue_green" {
  type    = bool
  default = false
}

variable "enable_codecommit" {
  type    = bool
  default = true
}

variable "enable_codebuild" {
  type    = bool
  default = true
}

variable "codebuild_image" {
  type    = string
  default = "aws/codebuild/standard:8.0"
}

variable "codebuild_compute_type" {
  type    = string
  default = "BUILD_GENERAL1_SMALL"
}

variable "log_retention_days" {
  type    = number
  default = 14
}

variable "alarm_email" {
  type    = string
  default = ""
}
