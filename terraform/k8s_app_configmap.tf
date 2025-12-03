resource "kubernetes_config_map" "preparation_api" {
  metadata {
    name      = "preparation-api-config"
    namespace = kubernetes_namespace.preparation_api.metadata[0].name
  }

  data = {
    APP_TITLE                          = var.app_title
    APP_VERSION                        = var.app_version
    APP_ENVIRONMENT                    = var.app_environment
    APP_ROOT_PATH                      = var.app_root_path
    AWS_REGION_NAME                    = var.region
    DATABASE_ECHO                      = tostring(var.database_echo)
    ORDER_API_BASE_URL                 = var.order_api_base_url
    PAYMENT_CLOSED_LISTENER_QUEUE_NAME = var.payment_closed_listener_queue_name
  }
}
