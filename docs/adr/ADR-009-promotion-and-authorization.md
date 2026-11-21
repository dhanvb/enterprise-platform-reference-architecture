# ADR-009: Separate Promotion Eligibility, Authorization and Deployment

**Status:** Accepted for reference architecture  
**Scope:** A05 environment promotion and production change control

## Context

A build passing tests does not demonstrate that its evidence is genuine, that a requester may deploy to production, or that a runtime is healthy. Combining these capabilities in an application-controlled pipeline grants excessive authority and undermines independent review.

## Decision

1. Separate the release registry, evidence verifier, advisory promotion evaluator, authorization service, desired-state change controller and runtime reconciler.
2. Evaluate a promotion against the exact `(releaseId, artifactDigest, applicationId, targetEnvironment, configurationRevision, onboardingSha256, policyVersion)` tuple.
3. Use independent authentication and authorization for the requester and required approvers. Do not accept approval fields from applicant-supplied JSON.
4. Restrict production deployment credentials to a controlled service acting on authorized desired state, not a general-purpose build job.
5. Deny or reject when evidence, identity, approvals or configuration bindings are missing, stale or inconsistent.
6. Treat rollback as a new governed change with current policy evaluation, not a rewrite of historical approval records.
7. Record separate outcomes for policy assessment, authorization, reconciliation and runtime verification.

## Alternatives

| Alternative | Rejected because |
|---|---|
| Single CI job builds and deploys to production | No independent authority boundary |
| Approval flag in application repository | Applicant can forge its own authorization |
| Successful tests imply deployment approval | Tests evaluate code, not actor/environment authority |
| GitOps reconciliation alone implies approval | Versioned desired state can still be changed without authorization |

## Consequences

**Benefits:** constrained privileges, auditable promotion decisions and defensible change authority boundaries.

**Costs:** separate identity/approval integrations, policies, authorization-to-commit binding, immutable audit logs, exception handling and operational procedures.

**Static demonstration boundary:** A05 `eligible` means selected submitted metadata is internally consistent. It is not a verified attestation, approval, reservation or permission to deploy.

## Evidence

- `contracts/delivery/promotion-request.schema.json`
- `contracts/delivery/decision.schema.json`
- `contracts/delivery/test_delivery.py`
- `docs/decisions/delivery-risk-register.csv`

Related: [ADR-005](ADR-005-onboarding-approval-and-lifecycle.md), [ADR-006](ADR-006-capacity-admission.md), [ADR-008](ADR-008-release-artifact-identity.md).
