
# ADR-003: Use a Declarative, Versioned Onboarding Contract

**Status:** Accepted for reference architecture  
**Date:** 2026-11-03  
**Related:** ARC-007, HLD-002, ADR-001

## Context

Ad hoc tickets and human conversations make application onboarding hard to validate, compare and audit. The platform needs a durable interface that survives changes to the request portal and infrastructure automation.

## Decision

Represent desired application platform consumption as a versioned, machine-readable, reviewed declaration.

Validate with JSON Schema, apply separate policy and authorization gates, bind approvals to an immutable revision digest, and keep the schema independent of Kubernetes product-specific manifests.

## Alternatives

1. **Unstructured service tickets:** familiar but inconsistent and difficult to check automatically. Not selected as the contract itself.
2. **Portal form as the source of truth:** user-friendly but couples business meaning to a front end and makes version history less portable. A portal may generate the contract later.
3. **Kubernetes manifests as intake:** immediately executable but leaks implementation detail and cannot represent independent governance safely. Not selected.
4. **Declarative versioned contract:** selected for reviewability, portability and automation readiness.

## Consequences

**Benefits:** diffable reviews, deterministic static checks, source control and governance traceability.

**Costs:** schema migration, developer training, compatibility/version policy, and translating abstract requests into runtime resources.

Validation alone cannot authorize or provision anything.

## Verification

Schema examples and tests in `contracts/onboarding/` provide limited static evidence. No production intake system is claimed.
