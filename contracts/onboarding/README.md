
# A03 Onboarding Contract v1

The contract describes the desired consumption of platform capabilities, not a Kubernetes resource or an approved deployment.

See [ARC-007](../../docs/architecture/07-application-onboarding-contract.md).

## Files

- `schema.json`: JSON Schema Draft 2020-12; version `platform.example.org/v1`.
- `../examples/valid-production.json`: expected structurally valid example; **not evidence of approval**.
- `../examples/invalid-missing-ownership.json`: expected invalid example, lacks `owner`.
- `test_contract.py`: focused unittest checks and cross-field policy illustration.
- `requirements-test.txt`: test dependencies with bounded version ranges.

## Contract semantics

- `metadata.revision` increments for each proposed content change; production approval must be bound separately to an immutable content digest and user identity.
- `owner.accountableEmail` is an applicant assertion, **not** proof of team membership or email control.
- `target.serviceTier` is a request, **not** an SLA commitment.
- CPU quantities use cores (for example `1`) or millicores (`250m`). Memory quantities use binary units (`Mi`, `Gi`, etc.).
- Requests must not exceed limits. This cross-field check is performed by the **Python policy helper**, not by JSON Schema.
- `data.stateful=false` implies `storageGiB=0`; `true` implies positive storage request.
- `critical` tier is only structurally allowed in production; the platform must still authorize it.
- No `approval`, credentials, tokens, raw secret values, Kubernetes RBAC grants or explicit namespace values are allowed.

## How to run

From the repository root (Python 3.10+):

```bash
python -m pip install -r contracts/onboarding/requirements-test.txt
python -m unittest discover -s contracts/onboarding -p 'test_contract.py' -v
python -m pytest validation/tests/test_a03.py -v
```

The built-in `unittest` suite uses `jsonschema` and supports strict `format` checking through `FormatChecker`.

**Schema validation alone is insufficient:** it cannot verify the requester's identity, authorization, available quota, network enforcement or disaster recovery.

## Evolution

Breaking changes require a new contract `apiVersion`, migration guide and compatibility tests.

Do not repurpose a v1 field's meaning silently.

A production policy engine and authenticating admission interface are intentionally out of scope.
