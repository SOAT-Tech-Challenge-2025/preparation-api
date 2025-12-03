variable "region" {
  description = "The AWS region to deploy resources in"
  default     = "us-east-1"
}

variable "force_rollout" {
  description = "A dummy variable to force redeployment of resources"
  type        = string
  default     = ""
}

variable "docker_api_image" {
  description = "The Docker image for the Preparation API"
  default     = "public.ecr.aws/p6c0d2v5/fiap-soat-techchallenge-preparation:latest"
}

variable "app_title" {
  description = "The title of the Preparation API"
  default     = "SOAT Tech Challenge Preparation API"
}

variable "app_version" {
  description = "The version of the Preparation API"
  default     = "1.0.0"
}

variable "app_environment" {
  description = "The environment for the Preparation API"
  default     = "production"
}

variable "app_root_path" {
  description = "The root path for the Preparation API"
  default     = "/soat-fast-food"
}

variable "aws_account_id" {
  description = "The AWS account ID to interact with AWS services"
  sensitive   = true
}

variable "aws_access_key_id" {
  description = "The AWS access key ID to interact with AWS services"
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "The AWS secret access key to interact with AWS services"
  sensitive   = true
}

variable "database_address" {
  description = "The address of the Postgres instance"
  sensitive   = true
}

variable "database_name" {
  description = "The database name in the Postgres instance"
  sensitive   = true
}

variable "database_port" {
  description = "The port for the Postgres instance"
  default     = 5432
}

variable "database_user" {
  description = "The username for the Postgres instance"
  sensitive   = true
}

variable "database_password" {
  description = "The password for the Postgres instance"
  sensitive   = true
}

variable "database_echo" {
  description = "Determine if SQLAlchemy should log SQL queries"
  type        = bool
  default     = false
}

variable "order_api_base_url" {
  description = "The base URL of the Order API"
}

variable "order_api_timeout" {
  description = "The timeout for requests to the Order API in seconds"
  type        = number
  default     = 10
}

variable "payment_closed_listener_queue_name" {
  description = "The name of the SQS queue to listen for payment closed events"
}
