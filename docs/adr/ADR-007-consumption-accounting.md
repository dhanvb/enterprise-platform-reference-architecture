
# ADR-007: Separate Commitments, Runtime Configuration and Usage for Showback

**Status:** Accepted for reference architecture  
**Decision scope:** Consumption accounting design; metering and billing are not implemented

## Context

A declared resource request, an accepted reservation, an enforced runtime limit and observed usage are not interchangeable quantities. Treating one as another produces misleading utilization and cost figures. Shared platform overhead and persistent storage replication further complicate attribution.

## Decision

Maintain four distinct conceptual records:

1. **Declared demand:** normalized requirements from the versioned A03 contract.
2. **Committed allocation:** resources recorded by a future authoritative reservation ledger, scoped to verified team, application and environment.
3. **Enforced configuration:** independently verified settings in the execution platform.
4. **Observed usage:** measurements for a stated interval, with source, completeness and time boundaries.

Use the verified team-to-application mapping, not an unverified applicant label, to attribute commitments and usage. Describe allocation-based showback separately from usage-based showback. Any financial model must use an approved rate card and explicitly state excluded expenses (for example backups, network transfer and shared services).

The A04 static evaluator outputs **declared demand and advisory eligibility only**. Its snapshot `committed` fields are supplied test inputs, not records it creates. It performs no metering, reservations, billing or reconciliation.

## Alternatives

| Alternative | Rejection rationale |
|---|---|
| Bill using CPU and memory limits | Limits are upper bounds, not actual usage or necessarily reserved capacity |
| Bill using observed usage alone | Ignores reserved capacity and missing-metering periods |
| Treat request as commitment | Does not prove acceptance or provisioning |
| Use application labels alone for ownership | Labels may be changed or forged |

## Consequences

**Benefits:** explainable showback, auditability, better capacity planning and explicit uncertainty.

**Tradeoffs:** requires a metering pipeline, authoritative ownership records, reconciliation and rate-card governance.

**Open questions:** sampling interval, shared-cost allocation, usage aggregation rules, storage replication multiplier, rate-card ownership, missing-data treatment and financial reporting controls.

## Validation boundary

Static tests cover demand calculation and decision metadata only. No measured utilization, actual platform commitment, usage attribution or cost figure is validated in A04.

## Related records

[ADR-006](ADR-006-capacity-admission.md), [A04 architecture](../architecture/08-platform-consumption-model.md).
