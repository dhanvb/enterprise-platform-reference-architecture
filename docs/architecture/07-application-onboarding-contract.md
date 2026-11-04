
# ARC-007: Application Onboarding Contract and Platform Consumption Model

**Status:** Proposed reference design  
**Phase:** A03  
**Related:** [Platform capability model](03-capability-model.md), [HLD-002](../hld/HLD-002-application-onboarding.md), ADR-003 through ADR-005

## 1. Problem and context

The reference enterprise operates approximately 100 services across 20 application teams and development, staging and production environments. These numbers are design assumptions, not observed fleet data. Informal platform requests omit ownership, capacity, ingress, sensitivity and recovery expectations; each request becomes a bespoke negotiation and cannot be reviewed consistently.

## 2. Intent and scope

Define a **declarative, versioned application onboarding contract** describing what a workload needs, the accountable owner, requested service levels and the governance checks preceding platform resource creation. The contract expresses intent, not an implementation-specific Kubernetes manifest or a guarantee of service levels.

In scope: application/environment identity, ownership, workload sizing, connectivity, data classification, statefulness, operational contacts, availability and recovery objectives, security requirements, lifecycle and auditability. Out of scope: application code, deployment pipeline selection, secrets values, business data migration and actual production availability guarantees.

## 3. Stakeholders and boundaries

| Actor | Accountable for | Not implicitly responsible for |
|---|---|---|
| Application team | Code, application dependencies, workload sizing, app health, data classification declaration, app restore procedures | Cluster control plane and platform policy |
| Platform engineering | Published capabilities, guardrails, platform resource provisioning, platform telemetry, platform runtime operations | Application functionality or business-data correctness |
| Security/governance | Risk classification, policy, authorized exceptions, production gate | Writing the application's configuration |
| Service owner | Business accountability and accepted service requirements | Bypassing mandatory security controls |

Identity of the requester must be independently authenticated; the `owner` field in a file is *a claim*, not proof of authorization.

## 4. Contract domains

| Domain | Minimum information | Reason |
|---|---|---|
| Contract | `apiVersion`, `kind`, application ID | Versioned parsing and traceability |
| Ownership | Team ID, accountable owner email, support contact | Escalation and responsibility |
| Target | Environment and service tier | Policy selection |
| Capacity | CPU/memory requests and limits, replicas | Capacity admission |
| Connectivity | Exposure classification and port | Reachability review |
| Data | Classification, stateful flag, storage request | Isolation and retention decision |
| Operations | Health endpoints, RTO, RPO | Readiness and recovery discussion |

Exact keys and restrictions are specified in [schema.json](../../contracts/onboarding/schema.json). No credential, token, private key or secret value is allowed in the declaration.

## 5. Lifecycle and state semantics

`Draft -> Submitted -> StructurallyValid -> PolicyEvaluated -> Approved -> Provisioning -> Verified -> Active`.

Requests may instead enter `Rejected`, `NeedsChanges`, `ProvisioningFailed`, `VerificationFailed`, or `Decommissioned`. These are logical states, not fields asserted by the untrusted applicant.

- Structural validation verifies syntax and shape only.
- Policy evaluation verifies allowed combinations and documented limits.
- Authorization verifies the caller's team/environment permissions and independent production approval.
- Provisioning consumes a **specific approved immutable revision**; retries must be idempotent.
- Verification tests the created resources against acceptance criteria before handoff.
- Changes create another contract revision and require reevaluation; destructive changes need specific approval.

See [HLD-002](../hld/HLD-002-application-onboarding.md) and [workflow](../assets/diagrams/src/04-onboarding-workflow.dot).

## 6. Functional and control requirements

| ID | Requirement | Verification |
|---|---|---|
| A03-R01 | Require application identity, owner and environment | Negative schema test |
| A03-R02 | Validate resource quantity formats and request/limit relationships | Schema and policy tests |
| A03-R03 | Reject undeclared contract properties using closed-field schema validation | JSON Schema negative tests |
| A03-R04 | Distinguish schema validity from authorization | Architecture review and integration test (pending) |
| A03-R05 | Explicit production authorization tied to contract digest | Integration test (pending) |
| A03-R06 | Enforce tenant isolation with multiple independent controls | Runtime tests (pending) |
| A03-R07 | Record provision/verification events with revision and actor | Audit integration test (pending) |
| A03-R08 | Require operational and recovery information | Schema test |
| A03-R09 | Reject invalid policy combinations | Unit test |
| A03-R10 | Preserve contract versioning and auditable changes | Repository and integration review |
| A03-R11 | Detect and prevent credential exposure within permitted contract text fields | Secret scanning and negative tests (pending) |

## 7. Acceptance and evidence levels

**Level 1, design:** architecture, ADRs, schema and traceability exist.

**Level 2, static:** example documents pass/fail as expected and policy rules run.

**Level 3, integration:** authenticated approvals, revision binding, idempotency and audit logs are exercised.

**Level 4, runtime:** tenant isolation, network policy, resource admission, restore and operational alerts are tested in a nonproduction cluster.

A03 currently targets Levels 1 and 2 only.

## 8. Explicit non-guarantees

Namespaces are organizational boundaries, not complete tenant isolation; network policy depends on a working enforcing dataplane; backups require restore exercises; resource limits do not prove performance; RTO/RPO values here are applicant objectives, not accepted SLAs.

## 9. Decisions and follow-up

- [ADR-003](../adr/ADR-003-declarative-onboarding-contract.md): a machine-readable declarative contract.
- [ADR-004](../adr/ADR-004-tenancy-and-isolation.md): risk-based tenancy boundary.
- [ADR-005](../adr/ADR-005-onboarding-approval-and-lifecycle.md): gates and lifecycle ownership.
- Remaining: authenticated API, policy engine, identity integration, deployment adapter and runtime conformance tests are **future implementation work**.
