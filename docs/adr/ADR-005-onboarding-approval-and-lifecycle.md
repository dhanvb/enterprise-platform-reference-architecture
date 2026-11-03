
# ADR-005: Separate Validation, Authorization, Provisioning and Activation

**Status:** Accepted for reference architecture  
**Date:** 2026-11-03  
**Related:** ARC-007, HLD-002

## Context

A well-formed declaration can still request an unauthorized production environment, excessive capacity or impermissible data exposure.

A workflow must not interpret `valid JSON` as `safe to deploy`.

## Decision

Enforce independently recorded phases: submission, schema validation, policy evaluation, authenticated authorization, idempotent provisioning, runtime verification and operational handoff.

Approval binds to request ID, actor, policy version, environment, expiration and content digest.

User-submitted documents cannot self-approve.

Production changes require a different authorized identity or documented exception to separation-of-duties policy.

## Alternatives

- **Direct deploy on schema pass:** rejected because schema is not an authorization engine.
- **Manual ticket approvals without revision binding:** rejected as vulnerable to stale approvals and ambiguous changes.
- **Explicit phased gates with immutable revision binding:** selected, despite greater workflow complexity.

## Consequences

The system needs identity integration, durable state, idempotent reconciliation, audit retention and failure states.

Revocation and destructive decommissioning require distinct controlled operations.

No workflow service has been implemented as part of static A03 evidence.

## Verification

Unit tests prove some policy invariants; they do not test authenticated approvers, event persistence, replay prevention or resource provisioning.

Those require integration evidence.
