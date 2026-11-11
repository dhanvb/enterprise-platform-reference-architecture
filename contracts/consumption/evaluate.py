"""A04 offline advisory capacity evaluator. NOT a reservation or authorization service."""

import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
KEYS = ("cpuRequestMilli", "memoryRequestKi", "storageGiB")


class EvaluationError(ValueError):
    """Unusable request or snapshot: do not produce an eligibility decision."""


def read_json(path):
    def unique_pairs(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise EvaluationError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    try:
        with Path(path).open(encoding="utf-8") as stream:
            return json.load(
                stream,
                object_pairs_hook=unique_pairs,
                parse_constant=lambda c: (
                    _ for _ in ()
                ).throw(EvaluationError(f"invalid JSON number: {c}"))
            )
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationError(str(exc)) from exc


def validate(document, schema_path):
    schema = read_json(schema_path)
    Draft202012Validator.check_schema(schema)
    errors = list(
        Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(document)
    )
    if errors:
        first = sorted(
            errors,
            key=lambda e: (list(map(str, e.path)), e.message)
        )[0]
        raise EvaluationError(
            f"schema validation failed: {first.message}"
        )


def cpu_milli(quantity):
    if re.fullmatch(r"[1-9][0-9]*m", quantity):
        return int(quantity[:-1])

    if not re.fullmatch(
        r"[1-9][0-9]*(?:\.[0-9]+)?", quantity
    ):
        raise EvaluationError("invalid CPU quantity")

    value = Decimal(quantity) * 1000

    if value != value.to_integral_value():
        raise EvaluationError(
            "CPU value contains fractional millicores"
        )

    return int(value)


def memory_ki(quantity):
    match = re.fullmatch(
        r"([1-9][0-9]*)(Ki|Mi|Gi|Ti)", quantity
    )
    if not match:
        raise EvaluationError("invalid memory quantity")

    return int(match.group(1)) * 1024 ** {
        "Ki": 0,
        "Mi": 1,
        "Gi": 2,
        "Ti": 3
    }[match.group(2)]


def resource_demand(declaration):
    workload = declaration["workload"]
    replicas = workload["replicas"]
    r = workload["resources"]

    cpu_request = cpu_milli(r["cpuRequest"])
    cpu_limit = cpu_milli(r["cpuLimit"])
    memory_request = memory_ki(r["memoryRequest"])
    memory_limit = memory_ki(r["memoryLimit"])

    if cpu_request > cpu_limit or memory_request > memory_limit:
        raise EvaluationError(
            "resource request exceeds resource limit"
        )

    if (
        declaration["data"]["classification"] == "restricted"
        and declaration["network"]["exposure"] == "public"
    ):
        raise EvaluationError(
            "restricted data cannot request public exposure"
        )

    return {
        "cpuRequestMilli": replicas * cpu_request,
        "memoryRequestKi": replicas * memory_request,
        "storageGiB": declaration["data"]["storageGiB"],
        "cpuLimitMilli": replicas * cpu_limit,
        "memoryLimitKi": replicas * memory_limit,
    }


def subtract(a, *others):
    return {
        key: a[key] - sum(item[key] for item in others)
        for key in KEYS
    }


def digest(declaration):
    # Demo canonicalization: sorted JSON keys and compact UTF-8 encoding.
    # Not a substitute for an interoperable canonical JSON standard.
    binary = json.dumps(
        declaration,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False
    ).encode("utf-8")

    return hashlib.sha256(binary).hexdigest()


def evaluate(declaration, snapshot):
    validate(
        declaration,
        ROOT / "contracts/onboarding/schema.json"
    )
    validate(
        snapshot,
        HERE / "capacity-snapshot.schema.json"
    )

    if (
        declaration["target"]["environment"]
        != snapshot["environment"]
    ):
        raise EvaluationError(
            "snapshot environment does not match request"
        )

    if (
        declaration["owner"]["teamId"]
        != snapshot["team"]["teamId"]
    ):
        raise EvaluationError(
            "declared team does not match supplied policy team"
        )

    team = snapshot["team"]
    capacity = snapshot["capacity"]

    if any(
        team["committed"][k] > team["entitlement"][k]
        for k in KEYS
    ):
        raise EvaluationError(
            "team commitments exceed entitlement"
        )

    if any(
        team["committed"][k] > capacity["committed"][k]
        for k in KEYS
    ):
        raise EvaluationError(
            "team commitments exceed environment commitments"
        )

    environment_headroom = subtract(
        capacity["allocatable"],
        capacity["platformReserved"],
        capacity["safetyHeadroom"],
        capacity["committed"]
    )

    if any(value < 0 for value in environment_headroom.values()):
        raise EvaluationError(
            "environment capacity snapshot is overcommitted"
        )

    team_headroom = subtract(
        team["entitlement"],
        team["committed"]
    )

    demand = resource_demand(declaration)

    labels = (
        ("cpuRequestMilli", "CPU"),
        ("memoryRequestKi", "MEMORY"),
        ("storageGiB", "STORAGE")
    )

    reasons = []

    for key, label in labels:
        if demand[key] > team_headroom[key]:
            reasons.append(f"TEAM_{label}_EXCEEDED")

        if demand[key] > environment_headroom[key]:
            reasons.append(f"ENV_{label}_EXCEEDED")

    decision = {
        "apiVersion": "platform.example.org/consumption/v1",
        "kind": "CapacityDecision",
        "evaluationKind": "advisory",
        "applicationId": declaration["metadata"]["applicationId"],
        "revision": declaration["metadata"]["revision"],
        "declaredTeamId": declaration["owner"]["teamId"],
        "policyTeamId": team["teamId"],
        "environment": snapshot["environment"],
        "requestSha256": digest(declaration),
        "snapshotId": snapshot["snapshotId"],
        "policyVersion": snapshot["policyVersion"],
        "demand": demand,
        "teamHeadroom": team_headroom,
        "environmentHeadroom": environment_headroom,
        "status": "denied" if reasons else "eligible",
        "reasons": reasons,
    }

    validate(decision, HERE / "decision.schema.json")

    return decision


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--declaration", required=True, type=Path
    )
    parser.add_argument(
        "--snapshot", required=True, type=Path
    )

    args = parser.parse_args(argv)

    try:
        decision = evaluate(
            read_json(args.declaration),
            read_json(args.snapshot)
        )
    except (EvaluationError, ValueError) as exc:
        print(f"A04 input rejected: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(decision, indent=2))

    return 0 if decision["status"] == "eligible" else 3


if __name__ == "__main__":
    sys.exit(main())
