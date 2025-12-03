resource "kubernetes_secret" "preparation_api" {
  metadata {
    name      = "preparation-api-secret"
    namespace = kubernetes_namespace.preparation_api.metadata[0].name
  }

  type = "Opaque"

  data = {
    DATABASE_DSN          = local.database_dsn
    AWS_ACCOUNT_ID        = var.aws_account_id
    AWS_ACCESS_KEY_ID     = var.aws_access_key_id
    AWS_SECRET_ACCESS_KEY = var.aws_secret_access_key
    ORDER_API_BASE_URL    = var.order_api_base_url
    ORDER_API_TIMEOUT     = var.order_api_timeout
  }
}
