
# ADR-006: Independent Entitlements and Capacity Admission

**Status:** Accepted for reference architecture  
**Decision scope:** Advisory capacity assessment; transaction-safe reservation is future work

## Context

A03 validates application declarations but does not guarantee available capacity. A requesting team could exceed its allowed allocation even if an environment has free resources. Conversely, a permitted request can fail because environment headroom is insufficient. Neither application-supplied ownership nor a copied capacity file proves authorization.

## Decision

1. Use the canonical A03 declaration to derive CPU requests, CPU limits, memory requests, memory limits and total persistent storage demand.
2. Normalize CPU to exact integer millicores and memory to exact integer KiB. Reject fractional millicores rather than rounding.
3. Obtain team entitlements and environment capacity from a separate platform-controlled snapshot; treat the file-based fixture as test data, not authenticated governance data.
4. Evaluate **both** team entitlement headroom and environment capacity headroom for CPU requests, memory requests and storage.
5. Deny eligibility if any required dimension exceeds either headroom. Reject malformed, inconsistent or mismatched input without issuing an eligibility decision.
6. Produce an advisory decision bound to the declaration digest, revision, snapshot ID and policy version.
7. Do not grant deployment permission, reserve resources or claim quota enforcement based on the advisory result.
8. Require atomic compare-and-reserve operations, idempotency and revision-aware delta accounting before integrating this design with live provisioning.

## Alternatives

| Alternative | Reason not selected |
|---|---|
| Unlimited first-come allocation | No team governance; resource exhaustion risk |
| Namespace ResourceQuota alone | Enforces a runtime scope but does not provide enterprise-wide entitlement and capacity accounting |
| Environment capacity only | Does not enforce team-specific limits |
| Team quotas only | Does not account for physical headroom |
| Direct Kubernetes admission as the only policy | Ties architecture to one runtime and does not solve reservation transactions across environments |

## Consequences

**Benefits:** deterministic decisions, explicit ownership and capacity boundaries, explainable denials, portable policy interface.

**Costs:** a trusted entitlement source, timely snapshots, authoritative commitment ledger and transaction coordinator will be needed for production adoption.

**Risk:** two requests may be independently eligible against the same snapshot. Only commit-time concurrency control prevents both from consuming the same headroom.

## Static evidence and limits

- `contracts/consumption/evaluate.py` implements the offline advisory checks.
- `contracts/consumption/test_consumption.py` exercises selected positive and negative inputs.
- `docs/decisions/consumption-traceability.csv` records verification state.
- No authenticated entitlement lookup, reservation service or runtime quota enforcement has been tested.

## Related records

[ADR-003](ADR-003-declarative-onboarding-contract.md), [ADR-005](ADR-005-onboarding-approval-and-lifecycle.md), [ADR-007](ADR-007-consumption-accounting.md).
