
# Enterprise Platform Capability Model

**Document ID:** ARC-003  
**Status:** Reference Architecture  
**Related:** ARC-001, ARC-002, HLD-001, ADR-001

## Purpose

Define the capabilities required by an enterprise application platform independently of the products used to implement them.

A capability describes what the platform must be able to do.

A product describes one possible way to implement that capability.

## Reference Context

The platform supports multiple application teams, deployment environments, microservices and shared operational capabilities.

The architecture must remain understandable even if the runtime, delivery tools or hosting environment change.

## Capability Domains

| ID | Capability | Architectural responsibility |
|---|---|---|
| CAP-01 | Workload Runtime | Execute, schedule, scale and recover workloads |
| CAP-02 | Tenancy and Isolation | Separate teams, environments, resources and access |
| CAP-03 | Build and Verification | Produce software artifacts through controlled builds and tests |
| CAP-04 | Artifact Management | Store, identify, verify and retain deployment artifacts |
| CAP-05 | Deployment and Reconciliation | Apply authorized releases and manage desired state |
| CAP-06 | Identity, Security and Policy | Authenticate, authorize and enforce mandatory controls |
| CAP-07 | Observability and Reliability | Collect telemetry, measure reliability and support investigation |
| CAP-08 | Operations and Lifecycle | Upgrade, recover, maintain and govern the platform |

## Capability Dependencies

Capabilities cannot be designed independently.

Examples:

- CAP-02 depends on runtime, networking, identity and policy enforcement.
- CAP-04 depends on build identity, artifact storage and provenance controls.
- CAP-05 depends on artifact identity, configuration, authorization and runtime interfaces.
- CAP-07 depends on workload instrumentation and operational ownership.
- CAP-08 spans the lifecycle of all other capabilities.

## Implementation Independence

Candidate implementations may include Kubernetes distributions, OpenShift, cloud services, GitHub Actions, GitLab CI/CD, Argo CD, Flux and other products.

Those products are not the capability model.

They must be selected through a separate evaluation against confirmed requirements.

## Architecture Maturity

A capability can exist at four maturity levels:

| Level | Meaning |
|---|---|
| 0 | Not defined |
| 1 | Requirements and design documented |
| 2 | Implemented and technically verified |
| 3 | Operated and supported with observed evidence |

Architecture evidence initially targets Level 1.

Implementation and Operations phases will provide evidence for higher maturity.

## Supporting Documents

- [Capability Catalog](04-capability-catalog.md)
- [Platform Requirements](05-platform-requirements.md)
- [Technology Evaluation](06-technology-evaluation.md)
- [ADR-002](../adr/ADR-002-technology-selection.md)