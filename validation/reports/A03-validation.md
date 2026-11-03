
# A03 Validation Report

**Status:** Reference snapshot validated locally; user repository execution pending  
**Date:** 2026-11-03 (reference snapshot run)  
**Target:** Contract static verification, documentation checks and diagram syntax

## Preconditions

- Python 3.10+ installed
- `python -m pip install -r contracts/onboarding/requirements-test.txt`
- Graphviz `dot` installed (for diagram check)
- Run all commands from repository root

## Commands

```bash
python -m unittest discover -s contracts/onboarding -p 'test_contract.py' -v
python -m pytest validation/tests/test_a03.py -v
python -m pytest validation/tests/test_a02.py -v
dot -Tsvg docs/assets/diagrams/src/04-onboarding-workflow.dot -o /tmp/a03-onboarding-workflow.svg
```

On Windows PowerShell, replace the final output with `-o onboarding-workflow.svg`.

The checked-in `.dot` is the source; a rendered image is optional unless you choose to retain it as additional evidence.

## Reference snapshot run (separate from your own checkout)

| Check | Expected | Actual | Evidence link |
|---|---|---|---|
| Unit tests | 12 passing | 12 passed in supplied reference snapshot | Re-run in your local checkout |
| A03 repository tests | 5 passing | 5 passed in supplied reference snapshot | Re-run in your local checkout |
| Existing A02 regression tests | Existing suite passes | 4 passed in supplied reference snapshot | Re-run in your local checkout |
| DOT render | Exit code zero and readable SVG | Graphviz rendered SVG successfully in reference snapshot | Inspect locally |

## Boundaries

A successful test run proves only these static fixtures and documentation assertions.

It does **not** demonstrate actual approval, request authenticity, Kubernetes RBAC, network isolation, provisioning idempotency, workload health, backup or SLA compliance.

Never mark pending integration/runtime controls as passed.

## Reviewer sign-off

Reviewer: _Not assigned_  
Review date: _Not recorded_  
Decision: _Pending_

## Your independent verification

After copying files into your local repository, rerun the commands, record Python and Graphviz versions and paste terminal output or attach log files.

Do not treat the reference snapshot results as evidence that your local GitHub `main` branch passed.
