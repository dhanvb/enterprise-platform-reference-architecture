# HLD-004: Enterprise Software Delivery and Release Governance

**Status:** Proposed logical design  
**Architecture:** [ARC-009](../architecture/09-enterprise-software-delivery.md)  
**Decisions:** [ADR-008](../adr/ADR-008-release-artifact-identity.md), [ADR-009](../adr/ADR-009-promotion-and-authorization.md)

## 1. Design objective

Preserve the identity of a software artifact from build through production while keeping eligibility, authorization, deployment and runtime verification as separate trust decisions. A successful pipeline is not proof that an intended artifact is authorized or healthy.

## 2. Logical components and boundaries

| Component | Responsibility | Trust boundary |
|---|---|---|
| Application source repository | Versioned source and build definition | Application-controlled |
| Build service | Produce artifact and build execution metadata | Controlled build environment; future integration |
| Artifact registry | Store immutable digest-addressed artifacts | Registry access and retention controls; future integration |
| Release registry | Associate source, build, artifact and evidence references | Release metadata requires validation and attestation |
| Evidence verifier | Validate attestations, builder identity and test evidence | Independent trust roots; future integration |
| Promotion evaluator | Assess metadata consistency and environment policy | Offline demonstrator in A05 |
| Identity and authorization service | Authenticate requester and approvers; enforce separation of duties | Independent trusted authority; future integration |
| Desired-state repository | Preserve authorized artifact and configuration revisions | Protected change control; future integration |
| Deployment reconciler | Apply approved desired state | Restricted runtime credentials; future integration |
| Runtime verification and audit | Check intended vs observed artifact/readiness and retain outcomes | Runtime evidence; future integration |

## 3. Core flows

**Build:** source revision → controlled build → published artifact digest → release record with evidence references. A release record is a claim until the associated artifact and attestations are independently verified.

**Promotion:** applicant supplies release record, target environment and configuration revision → static contract validation → offline advisory assessment → independent evidence validation and production authorization (not implemented) → permitted desired-state update (not implemented).

**Deployment:** trusted controller reconciles permitted desired-state revision → platform observes artifact identity and readiness → stores deployment outcome. Reconciliation success and application readiness are separate checks.

**Rollback:** submit a new promotion/deployment request targeting a prior artifact and compatible configuration. Re-evaluate current policy and authorization. Historical release records are not edited.

See the [editable Graphviz source](../assets/diagrams/src/06-release-promotion.dot) and [rendered SVG](../assets/diagrams/svg/06-release-promotion.svg).

## 4. Contracts

| Contract | File | Producer → consumer |
|---|---|---|
| ReleaseRecord | `contracts/delivery/release.schema.json` | Build/release registry → evaluator |
| PromotionRequest | `contracts/delivery/promotion-request.schema.json` | Requester → evaluator |
| PromotionDecision | `contracts/delivery/decision.schema.json` | Offline evaluator → reviewer |
| A03 declaration | `contracts/onboarding/schema.json` | Application owner → platform |

The offline evaluator also binds a promotion request to the exact A03 declaration using the **existing A04 demonstration JSON digest algorithm**. This is not a standardized cross-language signing or authorization format. Any production protocol must define canonical serialization and a verified trust chain.

A04 capacity eligibility remains a separate advisory assessment. It is not a production approval or a committed reservation.

## 5. Explicit failure behavior

- Malformed or incomplete input: reject evaluation with an error, no decision issued.
- Application/release/artifact/configuration binding mismatch: `denied` advisory decision with a reason code.
- Missing, failed or wrong-subject declared evidence: `denied` advisory decision.
- Required policy version unsupported: reject invalid request.
- Unavailable authoritative evidence, identity or authorization systems: **production deployment must not proceed**, regardless of advisory result.
- Runtime artifact drift or failed readiness: do not record a verified deployment; initiate investigation or controlled rollback.

## 6. Authorization design (future implementation)

A real promotion gate must verify authenticated actor and approver identities, enforce separation of duties, bind approval to release ID, artifact digest, environment, configuration revision, policy version and change request, and enforce expiry/revocation. An applicant-controlled `approved` flag is prohibited.

Only trusted automation should have production deployment credentials. A pipeline cannot obtain that privilege simply by writing an eligible decision fixture.

## 7. Evidence and limitations

The A05 demonstrator proves only selected properties: JSON Schema compliance, A03 binding, digest equality, required evidence *claims*, deterministic advisory decisions and repository integrity. It does **not** fetch registry artifacts, verify signatures, authenticate users, check actual test runs or update a cluster. Record this boundary in [A05 evidence](../../evidence/A05.md) and the [validation report](../../validation/reports/A05-validation.md).
