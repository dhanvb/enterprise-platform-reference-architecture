# HLD-003: Platform Consumption and Capacity Admission

**Status:** Proposed logical design
**Predecessor:** HLD-002 Application Onboarding

## Problem

A valid A03 declaration does not prove that its requested CPU, memory and storage fit the team's resource entitlement or the target environment's available capacity. The platform needs a reproducible eligibility check without conflating eligibility with authorization or reservation.

## Logical components

| Component | Input | Responsibility | Trust classification |
|---|---|---|---|
| A03 declaration store | Versioned applicant submission | Provide exact requested state | Untrusted declaration |
| A03 schema and policy gate | Declaration | Validate structure and cross-field rules | Static verification only |
| Entitlement authority | Verified team and environment | Provide limits and existing commitments | Platform-controlled, future integration |
| Capacity source | Environment | Provide allocatable capacity, reservations and commitments | Platform-controlled, future integration |
| A04 evaluator | Valid declaration and snapshot | Normalize and compare headroom | Offline demonstrator |
| Decision record | Evaluation output | Explain result, policy version and request digest | Advisory evidence |
| Approval and reservation coordinator | Identity, approval, fresh capacity | Authorize and atomically commit allocation | Future integration |
| Provisioner and runtime | Approved committed allocation | Enforce requested resources and verify state | Future runtime evidence |
| Metering/showback | Runtime telemetry and authoritative ownership | Attribute measured usage and estimated costs | Future integration |

## Flow

1. A03 declaration undergoes schema and cross-field checks.
2. Platform-controlled entitlement and capacity sources produce a versioned snapshot.
3. A04 calculates whole-workload CPU/memory requests and limits and total declared persistent storage.
4. The evaluator compares CPU request, memory request and storage demand with independent team/environment headroom.
5. It returns `eligible` or `denied` with reason codes and input identities.
6. A separate future authorization gate must verify identity, approvals and immutable request content.
7. A future commit coordinator rechecks headroom under concurrency control and persists reservation changes.
8. Runtime provisioning, reconciliation, telemetry and billing occur only through separately implemented controls.

See [editable Graphviz diagram](../assets/diagrams/src/05-consumption-admission.dot).

## Input and output contracts

- Input workload: [A03 schema](../../contracts/onboarding/schema.json).
- Input capacity fixture: [A04 snapshot schema](../../contracts/consumption/capacity-snapshot.schema.json).
- Output assessment: [A04 decision schema](../../contracts/consumption/decision.schema.json).
- Evaluator: [offline Python implementation](../../contracts/consumption/evaluate.py).

Snapshot values are illustrative and manually provided. Their accuracy, freshness and authorization are not verified by the evaluator. `policyTeamId` matching `declaredTeamId` is a consistency check, not proof of ownership.

## Calculations

- `CPU milli = replicas × per-replica request millicores`.
- `Memory Ki = replicas × per-replica requested Ki`.
- `Storage GiB = data.storageGiB` (not multiplied by replicas).
- `Team headroom = entitlement - team committed`.
- `Environment headroom = allocatable - platform reserved - safety headroom - environment committed`.

All dimensions must remain nonnegative after subtraction. Snapshot fields must be mutually exclusive to prevent double counting. In particular, `capacity.committed` includes team workloads but does not include `platformReserved` or `safetyHeadroom`.

## Failure handling

Invalid input, schema/policy mismatch, team/environment mismatch or internally overcommitted snapshot: **reject assessment**, not eligible. A well-formed request that exceeds headroom: **denied**. A request fitting the snapshot: **eligible, advisory only**.

## Reservation and updates: future design

Allocate by verified `(teamId, applicationId, environment)` identity. Revise commitments using the difference between desired and previously committed resources. Apply concurrency-safe transactions and idempotency. Release resources only after verified runtime reconciliation; especially do not release persistent storage merely because declared storage was reduced.

## Security and evidence limits

A04 static validation proves selected computation and contract behavior, not identity verification, approval, atomic reservation, enforcement, monitoring completeness or cost accuracy. See [ADR-006](../adr/ADR-006-capacity-admission.md), [ADR-007](../adr/ADR-007-consumption-accounting.md), and the [risk register](../decisions/consumption-risk-register.csv).
