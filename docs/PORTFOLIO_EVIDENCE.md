# Portfolio Evidence

This repo demonstrates SRE operating mechanics around a small service: instrumentation, SLOs, alerting, runbooks, incident templates and failure scenarios.

## Verified Locally

```bash
python -m unittest discover -s tests
python synthetics/check_http.py --dry-run
python services/api/app.py
```

Sample synthetic dry-run output:

```text
synthetic check configuration is valid
```

## Reviewer Evidence

| Evidence | Location | What it proves |
|---|---|---|
| CI badge | `README.md` | Tests and synthetic dry-run run in GitHub Actions. |
| Instrumented service | `services/api/app.py` | Health, readiness, workload and Prometheus metrics endpoints. |
| Alerts | `observability/prometheus/alerts.yml` | Error-rate and latency alert examples. |
| Dashboard | `observability/grafana/dashboards/service-slo.json` | RED signal visualization. |
| SLO | `slo/demo-api.yaml` | Availability and latency objectives with error-budget policy. |
| Runbooks | `runbooks/` | High-error and high-latency incident response. |
| RCA templates | `incidents/templates/` | Post-incident learning process. |

## Screenshots And Proof To Capture

- GitHub Actions CI run.
- `/healthz`, `/readyz`, `/work` and `/metrics` terminal output.
- Prometheus targets page showing the demo API scrape.
- Prometheus alert rule page for error rate or latency.
- Grafana SLO dashboard.
- Failure injection command output and corresponding alert/dashboard change.
- Filled sample RCA using `incidents/templates/rca-template.md`.

Do not reuse screenshots from unrelated services.
