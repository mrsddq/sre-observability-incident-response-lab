# Failure Injection

Use these scenarios to practice incident handling.

## Error Spike

```bash
for i in $(seq 1 100); do curl -s "http://localhost:8000/work?fail=true" > /dev/null; done
```

Expected signal:

- Error rate alert fires.
- Error budget burn increases.
- Runbook points to recent deploys and dependency checks.

## Latency Spike

```bash
for i in $(seq 1 100); do curl -s "http://localhost:8000/work?delay_ms=900" > /dev/null; done
```

Expected signal:

- p95 latency alert fires.
- Dashboard shows latency without necessarily showing error growth.

## Readiness Failure

Set `FORCE_NOT_READY=true` and restart the service.

Expected signal:

- Kubernetes readiness removes pods from service endpoints.
- Synthetic checks may still pass against healthy replicas.
