
# A04: Advisory Capacity Consumption Contract

This folder extends [A03 onboarding](../onboarding/README.md) without replacing its JSON Schema. The Python code is an offline **assessment**, not an authenticated admission controller or a reservation system.

## Files

| File | Purpose |
|---|---|
| `capacity-snapshot.schema.json` | Validates a supplied team/environment capacity snapshot |
| `decision.schema.json` | Validates a traceable advisory result |
| `evaluate.py` | Normalizes declared resource demand and compares headroom |
| `test_consumption.py` | Tests exact conversions and selected policy outcomes |
| `examples/production-snapshot.json` | Synthetic capacity/entitlement fixture |
| `examples/eligible-decision.json` | Expected output using A03 `valid-production.json` |
| `examples/denied-decision.json` | Expected output after changing A03 CPU request to `3` and CPU limit to `4` |

## Commands from repository root

```bash
python -m pip install -r contracts/onboarding/requirements-test.txt
python contracts/consumption/evaluate.py --declaration contracts/examples/valid-production.json --snapshot contracts/consumption/examples/production-snapshot.json
python -m unittest discover -s contracts/consumption -p 'test_consumption.py' -v
```

The CLI returns exit code **0** for eligible, **3** for valid but denied, and **2** for rejected/malformed input. It writes a JSON decision to standard output for eligible and denied cases; errors go to standard error.

## Resource semantics

- CPU requests and limits: whole-workload integer millicores.
- Memory requests and limits: whole-workload integer KiB.
- Storage: A03 `data.storageGiB`, **not multiplied by replicas**.
- Team headroom: entitlement minus committed team allocation.
- Environment headroom: allocatable minus platform reserved minus safety headroom minus committed workload allocation.

Snapshot counters are assumed to be mutually exclusive. `capacity.committed` already includes the team workload commitments. The evaluator never alters those counters.

## Trust and limitations

The snapshot is manually supplied. The evaluator checks shape and internal consistency, **not** authenticity, freshness, actor identity or reservation races. The output `policyTeamId` is the team identifier in the supplied snapshot, not proof of verified ownership. A match against `declaredTeamId` only checks consistency.

`requestSha256` uses UTF-8 JSON with sorted keys, compact separators and `ensure_ascii=False`. It is deterministic for the repository's Python implementation, but is not an independently standardized canonical-JSON protocol for cross-language authorization. Never use the digest from this demonstrator as an approval token.

Change operations, atomic commitment, usage metering, billing and runtime quotas remain out of scope. See [HLD-003](../../docs/hld/HLD-003-platform-consumption.md).
