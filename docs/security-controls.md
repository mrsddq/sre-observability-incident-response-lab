# Security Controls

## Implemented

- Non-root Dockerfile user.
- Kubernetes resource limits and probes.
- Synthetic checks.
- CI unit tests.
- Optional Trivy config scan through `make security-scan`.

## Recommended Production Additions

- NetworkPolicy for API namespace.
- Pod Security Standards labels.
- Image vulnerability scanning as a blocking gate.
- Secret management for runtime configuration.
- mTLS or ingress authentication for non-public endpoints.

## Security Review Questions

- Which endpoints are public?
- Are metrics exposing sensitive values?
- Can the pod run as root?
- Are runbooks and incident notes free of credentials?
- How are alert webhooks and tokens stored?
