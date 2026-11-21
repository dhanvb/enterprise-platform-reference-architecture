# ADR-008: Immutable Release Artifact Identity

**Status:** Accepted for reference architecture  
**Scope:** A05 release records and promotion

## Context

Version tags are useful labels but can be modified. Building independently in staging and production can create different artifacts even from the same source revision. Source commit identity alone is therefore not sufficient to identify the bytes deployed to production.

## Decision

1. Record source revision, build execution and artifact digest as distinct identities.
2. Identify deployable OCI artifacts using a digest-pinned reference (`repository@sha256:...`); keep human-readable versions as optional labels, not deployment authority.
3. Build once and promote the **same digest** between environments. A rebuild creates a new release identity and must be re-evaluated.
4. Bind declared evidence to the artifact digest; verify artifact provenance and evidence authenticity independently before a real production release.
5. Version and approve environment configuration separately from application artifact identity.
6. Treat artifact digest equality as an integrity/identity check, **not** proof of trusted builder, secure dependencies or absence of vulnerabilities.

## Alternatives

| Alternative | Rejected because |
|---|---|
| Deploy mutable tags | Tag drift can change deployed bytes after testing |
| Rebuild separately per environment | Breaks artifact identity across environments |
| Deploy by source commit only | One commit can produce distinct build outputs |
| Use release version as identity | Human-readable version can alias different artifacts |

## Consequences

**Benefits:** deterministic artifact binding, clearer audit trail, stronger promotion invariants and rollback identity.

**Costs:** registry immutability/retention, digest resolution, provenance verification, release-record lifecycle and platform-specific multi-architecture image handling are required in production.

**Not verified here:** registry immutability, signature verification, trusted provenance, artifact retention and running workload identity.

## Evidence

- `contracts/delivery/release.schema.json`
- `contracts/delivery/evaluate.py`
- `contracts/delivery/test_delivery.py`
- `docs/decisions/delivery-traceability.csv`

Related: [ADR-003](ADR-003-declarative-onboarding-contract.md), [ADR-009](ADR-009-promotion-and-authorization.md).
