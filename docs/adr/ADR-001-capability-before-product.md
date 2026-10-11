# ADR-001: Define Platform Capabilities Before Selecting Products

## Status

Accepted

## Context

The platform is expected to evolve over a long lifecycle.

Products used for Kubernetes orchestration, CI/CD, GitOps,
observability, security and secrets management may change during
that lifecycle.

Designing the architecture directly around individual products
would increase implementation coupling.

## Decision

Platform architecture will first define required capabilities,
interfaces and operational characteristics.

Product selection will occur only after capability requirements
and decision criteria have been documented.

## Examples

Continuous reconciliation is an architectural capability.

Possible implementations include:

- Argo CD
- Flux

Container orchestration is an architectural capability.

Possible implementations include:

- Kubernetes services
- OpenShift

## Consequences

### Positive

- reduces product coupling;
- enables alternative implementations;
- improves lifecycle flexibility;
- separates architectural intent from implementation.

### Negative

- requires additional design effort before implementation;
- some product-specific optimizations may need later ADRs;
- abstraction cannot eliminate all vendor-specific behavior.

## Alternatives Considered

### Product-first architecture

Rejected because the long-term architecture would become
unnecessarily coupled to the initial implementation stack.