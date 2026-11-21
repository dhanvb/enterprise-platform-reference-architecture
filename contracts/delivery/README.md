# A05: Software Release and Promotion Contracts

A05 extends the existing [A03 declaration](../onboarding/schema.json) and does not replace [A04 capacity admission](../consumption/README.md). All files here form an **offline advisory demonstration**. None of the input documents confers deployment privileges.

## Files

| File | Role |
|---|---|
| `release.schema.json` | Source/build/artifact/evidence reference record |
| `promotion-request.schema.json` | Environment and configuration promotion request |
| `decision.schema.json` | Machine-readable advisory result |
| `evaluate.py` | Selected deterministic consistency rules |
| `test_delivery.py` | Positive and negative contract tests |
| `examples/*.json` | Synthetic input and expected output fixtures |

## Commands (repository root)

```bash
python -m pip install -r contracts/onboarding/requirements-test.txt
python contracts/delivery/evaluate.py --release contracts/delivery/examples/release.json --request contracts/delivery/examples/production-promotion.json --declaration contracts/examples/valid-production.json
python -m unittest discover -s contracts/delivery -p 'test_delivery.py' -v
```

CLI exit codes: `0` = advisory eligible; `3` = valid request but advisory denied; `2` = rejected input/schema error. A CLI-eligible result never means authorized deployment.

## Contract semantics

- The release record is a **claim** about source, build and artifact identity.
- An artifact is addressed by an OCI digest. References and declared evidence subjects must refer to the same digest.
- Production, staging and development require selected evidence *claims* in the demo. The evaluator does **not** fetch or authenticate these claims.
- The promotion request binds an application, release, artifact, target environment, Git configuration revision, policy version and A03 declaration revision/digest.
- The A03 digest uses the existing A04 Python demonstration encoding (sorted JSON keys, compact UTF-8 JSON, `ensure_ascii=False`). It is **not** interoperable standardized JSON canonicalization and must not become a signing protocol.
- Release eligibility, trusted evidence verification, identity authorization, actual capacity reservation, desired-state change and runtime verification are separate steps.

## Production integration gaps

Trusted builder identities, registry digest resolution, attestation signatures, verified test results, SSO/RBAC, approver independence, expiring approvals, Git branch protection, protected deployment credentials, runtime drift checks and immutable audit storage are future integration requirements.

Architecture: [ARC-009](../../docs/architecture/09-enterprise-software-delivery.md) and [HLD-004](../../docs/hld/HLD-004-software-delivery.md).
