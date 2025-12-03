resource "kubernetes_deployment" "preparation_api" {
  metadata {
    name      = "preparation-api-deployment"
    namespace = kubernetes_namespace.preparation_api.metadata[0].name
  }

  spec {
    replicas = 1
    strategy {
      type = "Recreate"
    }
    selector {
      match_labels = {
        app = "preparation-api"
      }
    }

    template {
      metadata {
        labels = {
          app = "preparation-api"
        }

        annotations = {
          "restarted-at" = var.force_rollout
        }
      }

      spec {
        init_container {
          name              = "preparation-api-migrations"
          image             = var.docker_api_image
          image_pull_policy = "Always"
          working_dir       = "/app"
          command           = ["alembic", "upgrade", "head"]

          env_from {
            config_map_ref {
              name = kubernetes_config_map.preparation_api.metadata[0].name
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.preparation_api.metadata[0].name
            }
          }
        }

        container {
          name              = "preparation-api"
          image             = var.docker_api_image
          image_pull_policy = "Always"

          port {
            container_port = 8000
          }

          resources {
            limits = {
              cpu    = "500m"
              memory = "1Gi"
            }
            requests = {
              cpu    = "250m"
              memory = "512Mi"
            }
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.preparation_api.metadata[0].name
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.preparation_api.metadata[0].name
            }
          }
        }
      }
    }
  }
}
