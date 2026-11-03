
# HLD-002: Application Onboarding and Platform Consumption

**Status:** Proposed | **Phase:** A03 | **Implementation:** Technology-neutral

## Architecture drivers

A growing enterprise platform needs repeatable onboarding, accountable ownership, predictable resource allocation, policy enforcement and proof of authorized provisioning. The workflow must be independent of a particular portal, GitOps controller, cloud or Kubernetes vendor.

## Logical components

1. **Requester:** authenticated developer/team submits a versioned declaration.
2. **Contract repository/interface:** stores revisions; an application ID and revision digest identify an immutable submission.
3. **Schema validator:** parses, validates required keys, types, patterns and closed structures.
4. **Policy evaluator:** checks organizational quotas, classification, environment rules and resource relations.
5. **Authorization service:** evaluates user-to-team entitlement, segregation of duties, production approvals and exceptions; never trusts approval fields in applicant content.
6. **Provisioning orchestrator:** processes only authorized exact revisions, applies idempotent operations, stores state and reports failures.
7. **Execution platform:** implements runtime, isolation, networking, storage and operations.
8. **Verification and evidence store:** records what was requested, decided, created, tested, when and by whom.

The reference sequence is shown in [Graphviz DOT](../assets/diagrams/src/04-onboarding-workflow.dot).

## Data and control flow

| Step | Input | Output | Failure outcome |
|---|---|---|---|
| 1 Submit | Authenticated principal + declaration | Submission ID and digest | Reject unauthenticated caller |
| 2 Validate | Declaration | Structural result | Reject malformed/unknown fields |
| 3 Evaluate | Valid document + policy version | Allow/deny/warnings | NeedsChanges or Rejected |
| 4 Authorize | Principal, team entitlement, digest, environment | Signed/recorded authorization decision | No provisioning |
| 5 Provision | Approved digest + desired state | Platform resource references | Failed state, safe retry |
| 6 Verify | Resource references + approved contract | Evidence results | VerificationFailed, no active handoff |
| 7 Handoff | Verification success | Active record + ownership | Remain pending |

## Trust boundaries

- **Boundary A:** user-submitted declarations are untrusted input; parse strictly and never execute text.
- **Boundary B:** authorization data comes from an independent identity/approval system, not YAML or JSON supplied by a user.
- **Boundary C:** provisioning runs under narrowly scoped identities and cannot modify unrelated tenants.
- **Boundary D:** runtime tenant isolation requires RBAC, network policies, quotas, workload security and storage separation as applicable; namespace labels alone are not a boundary.
- **Boundary E:** audit evidence must be write-controlled, timestamped and correlate actor, decision, policy version, contract digest and target.

## Data contracts

The v1 declaration is JSON validated by [schema.json](../../contracts/onboarding/schema.json). Machine-readable keys and examples are documented in [contracts/onboarding/README.md](../../contracts/onboarding/README.md). The declaration contains references to secret stores, **not secret contents**.

JSON Schema does not establish identity, quota availability or actual platform resource enforcement.

## Availability, failure and retry

- Validation failure must not create resources.
- Authorization denial must not create resources.
- An orchestrator retry must use the same request ID and contract digest; duplicate invocations must not create duplicate tenants.
- Partial provisioning needs reconciliation and compensating actions; do not automatically delete persistent data on failure.
- Approved contract revision changes invalidate prior provisioning eligibility until re-approved.
- Revoked permissions, decommissioning and exceptions require a separately controlled lifecycle.

## Operational acceptance

Before `Active`, verify: expected identity/environment, isolation controls applied, resources match approved specification, reachable health endpoint where applicable, telemetry ownership labels and clear handoff.

Runtime acceptance requires a real implementation; this document does not assert it has occurred.

## Design options and consequences

See [ADR-003](../adr/ADR-003-declarative-onboarding-contract.md), [ADR-004](../adr/ADR-004-tenancy-and-isolation.md) and [ADR-005](../adr/ADR-005-onboarding-approval-and-lifecycle.md).

Portal/API/Git-based submission can all implement the same versioned contract. Policy and authorization responsibilities should remain separated even if deployed together.

## Threats and controls

| Threat | Required control | Evidence status |
|---|---|---|
| Forged owner/team | Verified identity + entitlement | Design only |
| Privilege escalation | Explicit authorization + least-privilege provisioner | Design only |
| Lateral tenant movement | Enforced network and identity boundaries | Runtime pending |
| Quota exhaustion | Resource admission checks and quotas | Runtime pending |
| Credential exposure | No plaintext secrets, secrets scanning | Scanner pending |
| Replay of approval | Bind approval to content digest + expiration | Integration pending |
| Hidden drift | Revision and runtime reconciliation | Integration pending |

## Traceability

[Requirements-to-evidence CSV](../decisions/onboarding-traceability.csv) and [risk register](../decisions/onboarding-risk-register.csv) establish what can and cannot yet be claimed.
