# ARC-008: Policy-Based Platform Consumption, Capacity Admission and Resource Governance

**Document ID:** ARC-008
**Status:** Proposed Reference Design
**Architecture Phase:** Architecture
**Evidence Level:** Design; static verification pending
**Reference Baseline:** A03 Application Onboarding Contract v1

## 1. Purpose

This document defines how an enterprise application platform interprets resource requirements submitted through the A03 onboarding contract and determines whether those requirements are eligible for platform capacity allocation.

The design covers:

- Resource demand calculation.
- Team-level consumption entitlements.
- Environment-level capacity availability.
- Capacity eligibility assessment.
- Resource reservation and enforcement boundaries.
- Resource consumption attribution.
- Consumption changes and lifecycle management.
- Policy versioning, auditability and failure handling.

The objective is to provide a consistent interface between application demand and platform resource governance.

The document describes a proposed reference architecture. It does not assert that a production admission controller, resource reservation service, metering pipeline or billing system has been implemented.

## 2. Architectural Context

The reference enterprise assumes approximately:

- 20 application teams.
- 100 deployable services.
- Development, staging and production environments.
- Shared platform capabilities.
- Both stateless and stateful workloads.
- Centrally governed security, capacity and operations.

These figures are scenario assumptions, not observed production measurements.

A03 establishes the application onboarding contract and separates structural validation, policy evaluation, authorization, provisioning and operational handoff.

However, a valid application declaration does not prove that the requested capacity is available or that the requesting team has sufficient resource entitlement.

For example, an application may request two replicas with the following resources per replica:

| Resource | Request | Limit |
|---|---|---|
| CPU | 250m | 1 core |
| Memory | 256Mi | 1Gi |

The aggregate workload requirements are:

- CPU requests: 500 millicores.
- CPU limits: 2000 millicores.
- Memory requests: 512 MiB.
- Memory limits: 2 GiB.

These quantities represent different operational concepts.

CPU and memory requests contribute to scheduler placement and capacity planning.

Resource limits constrain workload usage, subject to runtime enforcement.

Neither a valid declaration nor a calculated capacity requirement constitutes an approved or committed resource reservation.

A04 introduces the resource governance model required to address these distinctions.

## 3. Architectural Goals

### Goal 1: Deterministic Consumption Calculation

Equivalent valid workload declarations must produce identical normalized resource demand under the same calculation rules.

### Goal 2: Explicit Entitlement Boundaries

Each application team must have a separately governed resource entitlement.

An applicant must not be able to increase its entitlement by modifying the application declaration.

### Goal 3: Capacity-Aware Eligibility

The platform must evaluate resource demand against both team entitlement and the available capacity of the applicable environment.

### Goal 4: Separation of Eligibility and Authorization

A capacity-eligible request must not automatically receive deployment authorization.

Authentication, approval and governance requirements established by A03 remain independent.

### Goal 5: Traceable Resource Ownership

Every accepted resource allocation must be attributable to an application identity, environment and verified owning team.

### Goal 6: Technology-Neutral Governance

The consumption model must not depend on a particular Kubernetes distribution, cloud vendor, provisioning controller or billing product.

### Goal 7: Auditable Capacity Changes

Resource increases, reductions and releases must have identifiable requests, decisions and lifecycle records.

## 4. Scope and Exclusions

### In Scope

- CPU and memory resource normalization.
- Replica-based capacity calculation.
- Requested persistent storage capacity.
- Team and environment resource budgets.
- Capacity eligibility decisions.
- Capacity reservation requirements.
- Consumption reporting requirements.
- Change and decommissioning semantics.
- Static policy and calculation tests.

### Out of Scope

- Actual Kubernetes scheduler implementation.
- Production admission-controller deployment.
- Live cluster resource enforcement.
- Real-time resource metering integration.
- Production billing and invoicing.
- Commercial price or SLA commitments.
- Application-level performance guarantees.
- Deployment pipeline implementation.
- Business-data recovery verification.

These areas require implementation or operational evidence beyond the A04 architecture baseline.

## 5. Relationship to the A03 Contract

The canonical application-facing contract remains:

`contracts/onboarding/schema.json`

A04 must not independently redefine that contract.

The consumption model derives resource demand from the following A03 fields:

| A03 Field | A04 Interpretation |
|---|---|
| metadata.applicationId | Application allocation identity |
| metadata.revision | Requested declaration revision |
| owner.teamId | Claimed team ownership |
| target.environment | Requested environment |
| target.serviceTier | Requested service tier |
| workload.replicas | Declared replica count |
| workload.resources.cpuRequest | CPU requested per replica |
| workload.resources.cpuLimit | CPU limit per replica |
| workload.resources.memoryRequest | Memory requested per replica |
| workload.resources.memoryLimit | Memory limit per replica |
| data.stateful | Whether persistent application storage is requested |
| data.storageGiB | Total requested persistent capacity for the declared workload |

For this reference model, `data.storageGiB` represents total requested application persistent capacity, not storage multiplied by replica count.

This interpretation must remain explicit. Any future requirement for per-replica storage needs a separately versioned contract extension.

The `owner.teamId` property is a declaration supplied by the applicant. It is not proof of team membership or authorization.

The authenticated identity and verified team entitlement must come from independent trusted systems.

A04 does not change the semantics of A03 production approvals or service-tier requests.

## 6. Resource Consumption Model

### 6.1 CPU Requests

The total requested CPU is calculated as:

Total CPU Request =
Replica Count × CPU Request Per Replica

CPU quantities are normalized to integer millicores.

One CPU core equals 1000 millicores.

For example:

2 replicas × 250m = 500m

Decimal CPU quantities must be interpreted using exact decimal arithmetic.

The evaluator must not silently round a value containing a fractional millicore.

A quantity accepted by the A03 structural schema but not representable exactly in integer millicores must fail A04 normalization with an explicit reason.

### 6.2 CPU Limits

The aggregate CPU limit is:

Aggregate CPU Limit =
Replica Count × CPU Limit Per Replica

Aggregate CPU limits are not equivalent to capacity reservations.

A declared limit does not guarantee that every replica can simultaneously consume its maximum CPU allocation.

### 6.3 Memory Requests

The total requested memory is:

Total Memory Request =
Replica Count × Memory Request Per Replica

Memory quantities must be normalized using exact binary unit conversions.

Supported A03 memory quantities include Ki, Mi, Gi and Ti.

Internally, the evaluation model should preserve exact binary quantities, using integer KiB or bytes rather than floating-point approximations.

Example:

2 replicas × 256Mi = 512Mi

### 6.4 Memory Limits

Aggregate Memory Limit =
Replica Count × Memory Limit Per Replica

Memory requests and limits must remain distinct.

Memory consumption above an enforced container limit may result in workload termination.

The exact runtime outcome depends on the workload and enforcing platform.

### 6.5 Persistent Storage

Requested Persistent Storage =
A03 data.storageGiB

Persistent storage is evaluated independently from CPU and memory.

Persistent storage release must not be inferred solely from a lower value in a new declaration.

The platform must verify actual storage lifecycle state before considering previously committed capacity released.

Storage classes, replication factors, backup copies, snapshots and physical storage overhead are not modeled by the A03 storage field.

Those costs and physical-capacity effects require separate policies.

### 6.6 Resource Demand Vector

For capacity evaluation, each workload is represented by a normalized demand vector:

D = {
  cpuRequestMilli,
  memoryRequestKi,
  storageGiB
}

Aggregate CPU and memory limits are also calculated and retained for policy evaluation.

The demand vector represents requested capacity for the declared workload.

It does not represent observed resource usage.

## 7. Consumption Entitlements

A resource entitlement defines the maximum resource capacity that a verified team is permitted to reserve within a particular environment.

The entitlement is not supplied by an application applicant.

It must originate from an independently governed platform policy source.

For the reference model, entitlements are scoped by:

- Verified team identity.
- Environment.
- Policy version.

The entitlement contains maximum allowed resource requests for:

- CPU.
- Memory.
- Persistent storage.

A future design may extend the policy to include workload counts, resource tiers, regional placement and additional resource classes.

An entitlement is a consumption ceiling, not a guarantee that the physical environment has sufficient capacity.

## 8. Capacity Availability Model

The platform must distinguish two independent constraints.

### 8.1 Team Entitlement Headroom

Team entitlement headroom is the remaining resource capacity permitted by team policy.

For each resource dimension:

Team Headroom =
Team Entitlement - Existing Team Commitments

The proposed workload must fit within the remaining entitlement.

### 8.2 Environment Capacity Headroom

Environment capacity headroom is the capacity remaining after accounting for existing commitments and platform reservations.

Conceptually:

Environment Headroom =
Allocatable Capacity
- Platform/System Reservations
- Safety Headroom
- Existing Workload Commitments

The model must avoid subtracting the same reservation more than once.

The proposed workload must fit within environment headroom.

Capacity reserved for platform services and safety margins cannot be treated as ordinary application capacity.

### 8.3 Eligibility Rule

A request is capacity-eligible only when its resource demand satisfies both constraints.

For every governed resource dimension:

Requested Demand <= Team Headroom

AND

Requested Demand <= Environment Headroom

Failure in any mandatory resource dimension produces a capacity denial.

These calculations represent eligibility against a supplied snapshot.

They do not atomically reserve resources.

## 9. Capacity Admission Workflow

The proposed logical evaluation sequence is:

1. Receive an A03 onboarding declaration.
2. Validate its structure against the canonical A03 JSON Schema.
3. Apply the existing A03 cross-field policy checks.
4. Obtain trusted entitlement and capacity snapshot data.
5. Normalize declared workload resource quantities.
6. Calculate the complete workload demand vector.
7. Evaluate team entitlement headroom.
8. Evaluate environment capacity headroom.
9. Produce a deterministic capacity eligibility decision.
10. Record the evaluated declaration revision, policy version and snapshot identity.

The result of this evaluation is an advisory capacity decision.

It must not be represented as an authenticated approval, completed reservation or successful deployment.

A future integrated implementation must additionally:

- Verify the authenticated requester and authorization.
- Bind decisions to an immutable request digest.
- Revalidate capacity at commit time.
- Atomically reserve or update capacity.
- Provision resources through controlled identities.
- Verify runtime configuration.
- Record activation and reconciliation results.

Structural validation, eligibility, authorization and reservation remain distinct operations.

## 10. Consumption Decision Contract

A04 will introduce a machine-readable capacity assessment output.

The output must record:

| Field | Purpose |
|---|---|
| Contract version | Identify decision format |
| Application identity | Identify evaluated workload |
| Environment | Identify target environment |
| Declaration revision | Identify submitted version |
| Request digest | Bind evaluation to content |
| Policy version | Identify evaluated rules |
| Capacity snapshot ID | Identify capacity inputs |
| Normalized demand | Record calculated resources |
| Eligibility status | Eligible or denied |
| Reason codes | Explain failed policy checks |

A request digest must be calculated from a clearly defined canonical representation.

A digest without a documented canonicalization rule is not a reliable identity for a declaration.

The capacity decision must not contain credentials or raw secret values.

A capacity-eligible decision alone grants no provisioning privileges.

## 11. Resource Reservation Requirements

The reference architecture must support a future atomic reservation mechanism.

### 11.1 Reservation Identity

An allocation must be attributable to a stable logical key containing:

- Verified team ID.
- Application ID.
- Environment.

A specific declaration revision and digest identify the desired allocation state.

### 11.2 New Allocation

An accepted allocation must consume its demand from both the applicable team entitlement and environment capacity.

### 11.3 Allocation Change

A revised declaration must not automatically double-count the existing allocation.

The system must compare the proposed allocation against the currently committed allocation.

Conceptually:

Proposed Change =
New Total Demand - Existing Application Commitment

Both positive and negative changes require reconciliation.

A negative delta must not be released until the corresponding runtime resources have actually been reduced or removed safely.

### 11.4 Concurrent Requests

Two independently evaluated requests may each appear eligible against the same available-capacity snapshot.

Therefore, snapshot validation cannot prevent concurrent over-allocation.

The final reservation mechanism must provide atomic admission or an equivalent concurrency-safe transaction.

### 11.5 Idempotency

Retries for the same approved request and immutable revision must not create duplicate commitments.

Reservation state must be durable and reconcilable following partial failure.

The A04 static evaluator will not claim to provide these transaction guarantees.

## 12. Runtime Enforcement Boundary

A platform implementation may translate approved resource allocations into technology-specific controls.

For Kubernetes-based implementations, candidate mechanisms include:

- ResourceQuota.
- LimitRange.
- Workload resource requests and limits.
- Namespaces or equivalent workload scopes.
- Admission policy.
- Scheduler placement constraints.
- Resource usage telemetry.

These mechanisms have different responsibilities.

For example, a ResourceQuota can constrain namespace-level resource consumption, but it is not an enterprise entitlement ledger, a complete isolation boundary or a production billing system.

A successful static capacity assessment does not demonstrate that runtime policies are installed or enforced.

Those claims require implementation and runtime tests.

## 13. Consumption Measurement and Attribution

Resource governance must distinguish:

### Declared Demand

Resources specified by the application team.

### Committed Allocation

Resources accepted into the platform's authoritative reservation records.

### Enforced Configuration

Resource controls actually applied within the runtime environment.

### Observed Usage

Resources actually consumed over a measured time interval.

These quantities can differ significantly.

A04 proposes attribution using the verified ownership identity and application/environment allocation key.

Consumption reporting should provide:

- Application and owning team.
- Environment.
- Reporting interval.
- Committed resource allocation.
- Observed CPU consumption.
- Observed memory consumption.
- Persistent storage allocation.
- Metering source and collection period.

A reporting system must identify missing or incomplete telemetry.

Missing measurements must not automatically be interpreted as zero consumption.

## 14. Cost Attribution and Showback

The architecture must support transparent consumption attribution without requiring an immediate billing implementation.

Two reporting methods are distinguished.

### Allocation-Based Showback

Estimate the resource cost of committed capacity over a reporting interval.

Example conceptual formula:

Allocated Resource Cost =
Committed Resource Quantity
× Applicable Unit Rate
× Allocation Duration

### Usage-Based Showback

Estimate cost using observed resource consumption and a separately defined metering policy.

These approaches answer different questions.

Allocated capacity shows what a team has reserved.

Observed usage shows what a team actually consumes.

A billing or chargeback policy must explicitly identify which model applies.

Rates must come from an approved rate card.

A04 will not invent production rates or claim financial savings without supporting measurements.

Unmodeled infrastructure overhead, shared services, backups, network transfer and storage replication must be disclosed rather than silently omitted from a claimed total cost.

## 15. Failure and Lifecycle Scenarios

| Scenario | Required Architectural Behavior |
|---|---|
| Invalid resource quantity | Reject normalization |
| CPU request greater than limit | Reject through policy |
| Team entitlement exceeded | Capacity denial |
| Environment headroom insufficient | Capacity denial |
| Missing trusted entitlement | Fail closed |
| Missing capacity snapshot | Fail closed |
| Unknown environment | Reject evaluation |
| Changed application revision | Re-evaluate demand |
| Concurrent capacity requests | Require atomic commit-time control |
| Duplicate request | Prevent duplicate commitment |
| Partial provisioning | Preserve reconciliable state |
| Storage reduction | Release only after verified lifecycle action |
| Application decommissioning | Controlled and auditable release |
| Metering outage | Mark data incomplete |

An advisory eligibility result must never be used as the sole authority for destructive actions.

## 16. Security and Governance Boundaries

The design preserves the trust boundaries established in A03.

**Boundary A: Applicant Input**

The onboarding declaration is untrusted.

Schema validity does not prove ownership or entitlement.

**Boundary B: Platform Policy**

Entitlement and capacity information must be controlled by the platform or an authorized governance system.

An applicant must not modify these sources.

**Boundary C: Authorization**

Production deployment requires independent authorization tied to a specific immutable declaration revision.

**Boundary D: Reservation**

Committed allocations must be updated only by authorized, concurrency-safe operations.

**Boundary E: Runtime**

Resource configuration and tenant isolation must be verified against the actual platform.

**Boundary F: Audit and Metering**

Decisions, changes and measurements must have traceable identities, timestamps and provenance.

No A04 static test can independently verify these production trust boundaries.

## 17. Architecture Requirements

| ID | Requirement | Planned Verification |
|---|---|---|
| A04-R01 | Reuse canonical A03 onboarding schema | Compatibility test |
| A04-R02 | Normalize CPU and memory without silent rounding | Unit tests |
| A04-R03 | Calculate aggregate replica resource demand | Unit tests |
| A04-R04 | Evaluate team entitlement headroom | Positive and negative tests |
| A04-R05 | Evaluate environment capacity headroom | Positive and negative tests |
| A04-R06 | Reject missing or malformed trusted snapshots | Negative tests |
| A04-R07 | Produce traceable capacity decisions | Contract schema tests |
| A04-R08 | Preserve separation of eligibility and authorization | Architecture and integration review |
| A04-R09 | Require safe allocation updates and idempotency | Integration tests pending |
| A04-R10 | Prevent concurrent over-allocation | Integration tests pending |
| A04-R11 | Support committed-versus-observed consumption reporting | Metering integration pending |
| A04-R12 | Require runtime quota and resource enforcement evidence | Runtime tests pending |

All requirements must be mapped in the A04 traceability register.

Planned verification is not evidence of completion.

## 18. Architecture Decisions

The design will be governed by two new Architecture Decision Records.

### ADR-006: Capacity Admission and Entitlement Governance

Defines:

- Independent team entitlements.
- Two-level capacity evaluation.
- Resource normalization.
- Reservation and concurrency boundaries.
- Fail-closed behavior.

### ADR-007: Consumption Accounting and Cost Attribution

Defines:

- Committed allocation versus observed usage.
- Ownership-based attribution.
- Metering provenance.
- Allocation-based and usage-based showback.
- Limitations of financial cost estimates.

Both decisions must document alternatives, consequences and verification boundaries.

## 19. Planned Evidence

The A04 evidence package will contain:

- This architecture specification.
- Architecture Decision Records.
- A logical high-level design.
- An editable Graphviz diagram.
- Machine-readable capacity and decision contracts.
- Representative positive and negative examples.
- Python resource calculation and policy tests.
- Requirements traceability.
- A consumption risk register.
- Automated repository validation.
- A GitHub Actions execution record.
- An A04 evidence index.

## 20. Validation Strategy

Validation is divided into three levels.

### Level 1: Design Evidence

Architecture requirements, responsibilities, decisions and traceability are documented.

### Level 2: Static Evidence

Python tests validate calculation and selected policy invariants against controlled test fixtures.

JSON Schemas validate the intended machine-readable contract structures.

Repository checks validate selected evidence references and document consistency.

Graphviz verifies diagram syntax.

### Level 3: Integration and Runtime Evidence

Future testing must exercise:

- Authenticated team entitlement retrieval.
- Atomic reservation operations.
- Concurrent admission.
- Kubernetes quota enforcement.
- Live allocation reconciliation.
- Actual usage metering.
- Resource release.
- Auditable lifecycle transitions.

Level 3 is outside the initial A04 static evidence baseline.

## 21. Acceptance Criteria

The A04 architecture pack is ready for static-validation sign-off when:

- Architecture documents and decisions are complete.
- A03 compatibility tests pass.
- Resource conversion tests pass.
- Positive and negative capacity decisions are tested.
- Relevant decision contracts pass schema validation.
- Traceability and risk documentation are complete.
- The logical diagram renders successfully.
- Previous A02 and A03 tests remain passing.
- The A04 GitHub Actions workflow passes.
- The successful run and exact commit revision are recorded.
- Remaining implementation and runtime limitations are explicitly documented.

Passing these criteria establishes the static evidence baseline.

It does not establish a production-ready consumption-control plane.

## 22. Conclusion

A03 defines how an application team declares platform requirements and how onboarding responsibilities and approvals are separated.

A04 extends that foundation by establishing the resource-consumption governance model.

The critical distinction is that requested capacity, eligible capacity, committed capacity, enforced limits and observed consumption are separate concepts.

A reliable enterprise platform must preserve those distinctions throughout onboarding, provisioning, operation and decommissioning.

The architecture is therefore designed around independently governed entitlements, deterministic resource evaluation, traceable decisions and future concurrency-safe capacity commitments.

Static evidence will verify selected calculation and contract rules.

Actual reservation integrity, runtime enforcement and metering accuracy remain implementation responsibilities requiring separate evidence.