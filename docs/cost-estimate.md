# Cost Estimate

The lab runs locally with Docker Compose or on a small Kubernetes cluster.

## Local Demo

| Component | Cost |
|---|---:|
| Python service | Free |
| Docker Compose Prometheus/Grafana | Free except local resources |

## Kubernetes Demo

| Resource | Cost driver | Control |
|---|---|---|
| API pods | CPU and memory requests | Keep replicas low |
| Prometheus | Metrics retention | Use short retention in demos |
| Grafana | Persistent storage | Use ephemeral demo storage |

## Guardrails

- Keep demo clusters short-lived.
- Avoid managed cloud observability add-ons unless needed.
- Destroy demo namespaces after testing.
