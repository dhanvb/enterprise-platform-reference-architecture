# Architecture Principles

These principles guide the design of the Enterprise Platform Reference
Architecture.

They describe architectural intent rather than specific product choices.

---

## P01 - Capability Before Product

Architecture decisions should begin with the capability required by the
organization rather than the product used to implement it.

For example, the architectural requirement may be:

> Desired application state must be stored in version control and continuously
> reconciled with the runtime environment.

Argo CD and Flux are possible implementations of this capability.

The architecture should avoid unnecessary dependency on implementation-specific
behavior.

---

## P02 - Platform as a Product

The platform should be treated as a product consumed by application teams.

Application teams should receive documented interfaces, supported capabilities,
service expectations and onboarding mechanisms rather than a collection of
unrelated infrastructure components.

The platform team is therefore responsible for usability, reliability,
documentation, lifecycle management and continuous improvement.

---

## P03 - Standardize the Paved Road

The platform should provide a supported default path for common application
requirements.

This paved road should include standard approaches for:

- application onboarding
- software delivery
- security
- identity
- secrets
- observability
- deployment
- scaling

Teams may require exceptions, but exceptions should be deliberate rather than
becoming the default operating model.

---

## P04 - Clear Platform and Application Ownership

Responsibilities between application teams and the platform organization must
be explicit.

The platform team owns shared platform capabilities.

Application teams remain responsible for their application code, behavior,
dependencies and application-specific configuration.

Shared responsibilities must be documented rather than assumed.

---

## P05 - Build Once, Promote the Same Artifact

A workload should be built once and the same immutable artifact should be
promoted across environments.

Production artifacts should not be independently rebuilt from the same source
code.

This improves:

- reproducibility
- traceability
- rollback
- security
- auditability

---

## P06 - Declarative Desired State

Platform and workload configuration should be declaratively defined wherever
practical.

The intended state should be stored in version-controlled systems and compared
against actual runtime state.

This provides repeatability, reviewability and recovery from configuration
drift.

---

## P07 - Security by Default

The normal platform path should automatically apply appropriate security
controls.

Security should not depend on individual teams remembering separate manual
procedures.

Controls should be integrated into source governance, software delivery,
artifact management, deployment and runtime operation.

---

## P08 - Least Privilege

Humans and workloads should receive only the permissions required to perform
their responsibilities.

Administrative access should be limited, auditable and preferably temporary.

Workloads should use dedicated identities rather than shared long-lived
credentials wherever possible.

---

## P09 - Observability by Default

Workloads and platform components should produce sufficient telemetry to
understand system behavior.

The platform should support:

- metrics
- logs
- traces
- events

Application onboarding should include observability requirements rather than
adding monitoring after deployment.

---

## P10 - Failure and Recovery Are Design Requirements

Infrastructure and applications will fail.

The architecture must therefore consider failure detection, blast radius,
recovery and rollback during design.

Successful deployment alone is not proof of platform reliability.

Recovery must eventually be tested.

---

## P11 - Important Actions Must Be Auditable

Changes affecting production environments should leave evidence.

The platform should make it possible to determine:

- what changed
- who requested the change
- who approved it
- which source revision produced it
- which artifact was deployed
- when deployment occurred
- whether verification succeeded
- whether rollback occurred

---

## P12 - Operability Is Part of Architecture

The platform is not complete when workloads can be deployed.

It must also be possible to:

- monitor it
- troubleshoot it
- upgrade it
- recover it
- rotate credentials and certificates
- manage capacity
- transfer responsibility to another competent operations team

---

## P13 - Automate Repeatable Operations

Repeatable and deterministic platform operations should be automated where the
risk and implementation effort justify automation.

Automation reduces inconsistency but must itself remain observable,
version-controlled and recoverable.

---

## P14 - Minimize Implementation Coupling

Application teams should interact primarily with stable platform contracts.

They should not need to understand every implementation component underneath
those contracts.

This reduces the impact of replacing platform technologies.

---

## P15 - Design for Component Replacement

The platform is expected to evolve throughout its lifecycle.

CI/CD systems, orchestration platforms, security products and observability
systems may eventually be replaced.

Architectural boundaries should therefore make replacement possible without
requiring every application to be redesigned.