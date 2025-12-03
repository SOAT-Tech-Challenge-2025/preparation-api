resource "kubernetes_deployment" "payment_closed_listener" {
  metadata {
    name      = "payment-closed-listener-deployment"
    namespace = kubernetes_namespace.preparation_api.metadata[0].name
  }

  spec {
    replicas = 1
    strategy {
      type = "Recreate"
    }
    selector {
      match_labels = {
        app = "payment-closed-listener"
      }
    }

    template {
      metadata {
        labels = {
          app = "payment-closed-listener"
        }

        annotations = {
          "restarted-at" = var.force_rollout
        }
      }

      spec {
        container {
          name              = "payment-closed-listener"
          image             = var.docker_api_image
          image_pull_policy = "Always"
          command           = ["sh", "/app/docker-entrypoint/start_payment_closed_listener.sh"]

          resources {
            limits = {
              cpu    = "300m"
              memory = "256Mi"
            }
            requests = {
              cpu    = "100m"
              memory = "128Mi"
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
