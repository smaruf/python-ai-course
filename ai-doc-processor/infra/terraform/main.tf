terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "eu-west-1"
}

variable "db_password" {
  sensitive = true
}

# --- S3 bucket for raw document uploads ---
resource "aws_s3_bucket" "documents" {
  bucket = "ai-doc-processor-documents"
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id
  versioning_configuration {
    status = "Enabled"
  }
}

# --- RDS PostgreSQL with pgvector ---
resource "aws_db_instance" "main" {
  identifier        = "ai-doc-processor-db"
  engine            = "postgres"
  engine_version    = "16.2"
  instance_class    = "db.t4g.micro"
  allocated_storage = 20
  db_name           = "ai_doc_processor"
  username          = "postgres"
  password          = var.db_password
  skip_final_snapshot = true

  tags = {
    Project = "ai-doc-processor"
  }
}

# --- ElastiCache Redis for Celery ---
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "ai-doc-processor-redis"
  engine               = "redis"
  node_type            = "cache.t4g.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
}

output "db_endpoint" {
  value = aws_db_instance.main.endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.redis.cache_nodes[0].address
}
