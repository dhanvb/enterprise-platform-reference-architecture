
"""A03 repository integration checks, not live-cluster evidence."""

import csv
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]


def test_a03_architecture_artifacts_present():
    required = [
        "docs/architecture/07-application-onboarding-contract.md",
        "docs/hld/HLD-002-application-onboarding.md",
        "docs/assets/diagrams/src/04-onboarding-workflow.dot",
        "docs/adr/ADR-003-declarative-onboarding-contract.md",
        "docs/adr/ADR-004-tenancy-and-isolation.md",
        "docs/adr/ADR-005-onboarding-approval-and-lifecycle.md",
        "docs/decisions/onboarding-traceability.csv",
        "docs/decisions/onboarding-risk-register.csv",
    ]

    for p in required:
        assert (ROOT / p).is_file() and (ROOT / p).stat().st_size > 100, p


def test_a03_examples_schema():
    base = ROOT / "contracts"

    schema = json.loads(
        (base / "onboarding/schema.json").read_text(encoding="utf-8")
    )

    Draft202012Validator.check_schema(schema)

    validator = Draft202012Validator(
        schema, format_checker=FormatChecker()
    )

    valid = json.loads(
        (base / "examples/valid-production.json").read_text(encoding="utf-8")
    )
    invalid = json.loads(
        (base / "examples/invalid-missing-ownership.json").read_text(encoding="utf-8")
    )

    assert list(validator.iter_errors(valid)) == []
    assert list(validator.iter_errors(invalid)) != []


def test_a03_requirement_traceability():
    arch = (
        ROOT / "docs/architecture/07-application-onboarding-contract.md"
    ).read_text(encoding="utf-8")

    with (
        ROOT / "docs/decisions/onboarding-traceability.csv"
    ).open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 10
    assert len({r["requirement_id"] for r in rows}) == len(rows)

    for row in rows:
        assert row["requirement_id"] in arch
        assert row["verification_method"]
        assert row["evidence_status"] in {
            "Design",
            "Static verified",
            "Pending integration",
            "Pending runtime"
        }

        for path in row["evidence_path"].split(";"):
            assert (ROOT / path).exists(), path


def test_a03_risks_have_treatment():
    with (
        ROOT / "docs/decisions/onboarding-risk-register.csv"
    ).open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) >= 5
    assert len({r["risk_id"] for r in rows}) == len(rows)

    for row in rows:
        assert row["mitigation"] and row["verification_needed"]


def test_a03_readme_links():
    text = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "07-application-onboarding-contract.md" in text
    assert "HLD-002-application-onboarding.md" in text
