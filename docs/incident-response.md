# Incident Response

## SLOs And SLIs

| SLO | SLI | Alert path |
|---|---|---|
| 99.9% availability | successful requests / total requests | `DemoApiHighErrorRate` |
| p95 latency under 500 ms | latency histogram p95 | `DemoApiHighLatency` |

## Failure Scenarios

| Scenario | Command | Expected signal |
|---|---|---|
| Error spike | `curl /work?fail=true` loop | Error-rate alert |
| Latency spike | `curl /work?delay_ms=900` loop | Latency alert |
| Readiness failure | `FORCE_NOT_READY=true` | Kubernetes removes pod from service |

## Rollback Process

1. Identify last deployment or configuration change.
2. Revert the change or redeploy the previous image.
3. Confirm health checks, synthetic checks and alert recovery.
4. Capture timeline in `incidents/templates/timeline-template.md`.
5. Write RCA with action items.

## What I Would Improve In Production

- Add paging integration and alert routing.
- Add blackbox exporter synthetic checks.
- Add persistent logs through Loki or OpenSearch.
- Add automated rollback for failed rollout health.
- Add dashboards generated from code.
