# Architecture

The lab centers on a deliberately small HTTP service so the operational system is easy to inspect.

## Service

The service exposes:

- `/healthz` for liveness
- `/readyz` for readiness
- `/work` for simulated workload
- `/metrics` for Prometheus-compatible metrics

## Observability

Prometheus scrapes the service and evaluates alert rules. Grafana visualizes the main SRE signals: traffic, error rate, latency, and restarts.

## Incident Response

Alerts link to runbooks. Runbooks drive mitigation and data collection. RCA templates capture what happened, why it happened, what was done, and what should change.
