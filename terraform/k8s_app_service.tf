resource "kubernetes_service" "preparation_api" {
  metadata {
    name      = "preparation-api-service"
    namespace = kubernetes_namespace.preparation_api.metadata[0].name
  }

  spec {
    type = "ClusterIP"

    selector = {
      app = "preparation-api"
    }

    port {
      port        = 80
      target_port = 8000
    }
  }
}
