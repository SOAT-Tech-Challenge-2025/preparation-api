resource "kubernetes_horizontal_pod_autoscaler_v2" "preparation_api" {
  metadata {
    name      = "preparation-api-hpa"
    namespace = kubernetes_namespace.preparation_api.metadata[0].name
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.preparation_api.metadata[0].name
    }

    min_replicas = 1
    max_replicas = 3

    metric {
      type = "Resource"

      resource {
        name = "cpu"

        target {
          type                = "Utilization"
          average_utilization = 90
        }
      }
    }

    metric {
      type = "Resource"

      resource {
        name = "memory"

        target {
          type                = "Utilization"
          average_utilization = 90
        }
      }
    }
  }
}
