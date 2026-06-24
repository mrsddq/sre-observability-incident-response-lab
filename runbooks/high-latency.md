# Runbook: High Latency

## Impact

Users may see slow responses while requests still succeed.

## First Checks

1. Confirm p95 and p99 latency.
2. Compare latency with CPU and memory saturation.
3. Check upstream dependency latency.
4. Review request volume and queueing.

## Mitigation

- Roll back a latency-causing deploy.
- Reduce expensive code paths through feature flags.
- Scale horizontally if saturation is the driver.
- Add temporary caching if read paths dominate.

## Follow-Up

Turn the root cause into a dashboard panel, alert, or automated regression test.
