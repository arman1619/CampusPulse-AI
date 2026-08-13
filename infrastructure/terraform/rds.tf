resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnets"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}

resource "aws_db_instance" "postgres" {
  identifier = "${var.project_name}-${var.environment}"

  engine                       = "postgres"
  instance_class               = var.db_instance_class
  allocated_storage            = var.db_allocated_storage
  max_allocated_storage        = 50
  storage_type                 = "gp3"
  storage_encrypted            = true
  username                     = var.db_username
  password                     = local.db_password_effective
  db_name                      = "postgres"
  port                         = 5432
  publicly_accessible          = false
  multi_az                     = var.db_multi_az
  db_subnet_group_name         = aws_db_subnet_group.main.name
  vpc_security_group_ids       = [aws_security_group.rds.id]
  backup_retention_period      = 7
  backup_window                = "17:00-18:00"
  maintenance_window           = "sun:18:30-sun:19:30"
  skip_final_snapshot          = true
  deletion_protection          = var.rds_deletion_protection
  auto_minor_version_upgrade   = true
  performance_insights_enabled = false
  apply_immediately            = true
}
