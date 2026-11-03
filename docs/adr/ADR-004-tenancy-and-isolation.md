
# ADR-004: Treat Tenancy as a Risk-Based Isolation Decision

**Status:** Accepted for reference architecture  
**Date:** 2026-11-03  
**Related:** ARC-007, HLD-002

## Context

A shared platform must host workloads of different ownership and sensitivity. A tenant name or namespace alone does not contain privilege, network, storage, runtime or control-plane risks.

## Decision

Evaluate tenant boundary requirements using data classification, regulatory restrictions, trust level, workload privileges and blast-radius tolerance.

The default proposed shared-runtime model combines scoped identities/RBAC, namespace/project scoping, default-deny network policies, workload-security controls, quotas, secret separation and storage authorization.

Elevated-risk workloads may require dedicated nodes, clusters or accounts subject to policy; do not assume the shared platform can accept every workload.

## Alternatives

- **One shared namespace for all teams:** rejected for weak ownership/control boundaries.
- **Namespace per application/environment with layered controls:** default candidate for eligible workloads, only after enforcement is verified.
- **Dedicated cluster/account for every application:** stronger isolation potential but high operational and financial overhead; appropriate for some threat profiles, not universal.

## Consequences

Isolation becomes a policy and implementation concern, not a schema field alone. Higher isolation tiers cost capacity and operations.

Misconfigured CNI, RBAC, admission or storage can defeat nominal separation.

No isolation claim is validated until adversarial cross-tenant tests run against an actual deployed environment.

## Verification

Static examples assert requested classification and exposure only. Runtime RBAC, east/west traffic, egress, storage and privilege tests remain pending.
