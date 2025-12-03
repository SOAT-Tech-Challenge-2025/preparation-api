locals {
  api_gateway_url = data.terraform_remote_state.infra.outputs.api_gateway_url
  database_dsn    = "postgresql+asyncpg://${var.database_user}:${var.database_password}@${var.database_address}:${var.database_port}/${var.database_name}"
}
