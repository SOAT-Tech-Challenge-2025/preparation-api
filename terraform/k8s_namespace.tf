resource "kubernetes_namespace" "preparation_api" {
  metadata {
    name = "tech-challenge-preparation-api"
  }
}
