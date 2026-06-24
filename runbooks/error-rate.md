# Runbook: High Error Rate

## Impact

Users may receive failed responses from the API.

## First Checks

1. Confirm alert scope and affected environment.
2. Check recent deploys and configuration changes.
3. Compare error rate with request volume.
4. Review logs for repeated exception patterns.

## Mitigation

- Roll back the latest risky deploy.
- Disable the failing feature flag.
- Scale only if errors correlate with saturation.

## Evidence To Capture

- Alert start time.
- Error rate graph.
- Relevant logs.
- Deploy SHA and change owner.
- Customer impact estimate.
