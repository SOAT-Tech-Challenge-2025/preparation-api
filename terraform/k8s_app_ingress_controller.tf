resource "kubernetes_ingress_v1" "preparation_api" {
  metadata {
    name      = "preparation-api-route"
    namespace = kubernetes_namespace.preparation_api.metadata[0].name
  }

  spec {
    ingress_class_name = "nginx"

    rule {
      http {
        path {
          path      = "/soat-fast-food/v1/preparation"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service.preparation_api.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}
