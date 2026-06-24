# Runbook

## Prerequisites

- Python 3.11+
- Docker Compose for local stack
- kubectl for Kubernetes demo
- Prometheus/Grafana for full observability demo

## Validate

```bash
make test
make validate
```

## Local Demo

```bash
make run
curl http://localhost:8000/healthz
curl http://localhost:8000/work
curl http://localhost:8000/metrics
```

Full local stack:

```bash
make local-demo
```

## Deploy

```bash
make deploy
kubectl get pods -n sre-lab
```

## Destroy

```bash
make destroy
```

## Backup And Restore

- Keep dashboards, alerts, runbooks and RCA templates in Git.
- Export incident evidence to durable storage after a real incident.
- Restore service state from manifests rather than manual cluster edits.
