"""A04 repository/evidence structure checks.

These are static checks, not production runtime assertions.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "docs/architecture/08-platform-consumption-model.md",
    "docs/hld/HLD-003-platform-consumption.md",
    "docs/adr/ADR-006-capacity-admission.md",
    "docs/adr/ADR-007-consumption-accounting.md",
    "docs/assets/diagrams/src/05-consumption-admission.dot",
    "docs/decisions/consumption-traceability.csv",
    "docs/decisions/consumption-risk-register.csv",
    "contracts/consumption/README.md",
    "contracts/consumption/capacity-snapshot.schema.json",
    "contracts/consumption/decision.schema.json",
    "contracts/consumption/evaluate.py",
    "contracts/consumption/test_consumption.py",
    "contracts/consumption/examples/production-snapshot.json",
    "contracts/consumption/examples/eligible-decision.json",
    "contracts/consumption/examples/denied-decision.json",
    "validation/reports/A04-validation.md",
    "evidence/A04.md",
    ".github/workflows/a04-validation.yml",
]


def test_a04_required_files():
    for file in REQUIRED:
        path = ROOT / file

        assert (
            path.is_file()
            and path.stat().st_size > 20
        ), file


def test_a04_traceability():
    arch = (
        ROOT / "docs/architecture/08-platform-consumption-model.md"
    ).read_text(encoding="utf-8")

    with (
        ROOT / "docs/decisions/consumption-traceability.csv"
    ).open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 12

    assert {
        row["requirement_id"] for row in rows
    } == {
        f"A04-R{i:02d}" for i in range(1, 13)
    }

    allowed = {
        "Design",
        "Pending static verification",
        "Pending integration",
        "Pending runtime"
    }

    for row in rows:
        assert row["requirement_id"] in arch
        assert row["verification_method"]
        assert row["evidence_status"] in allowed

        for item in row["evidence_path"].split(";"):
            assert (ROOT / item).exists(), item


def test_a04_risks():
    with (
        ROOT / "docs/decisions/consumption-risk-register.csv"
    ).open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) >= 7

    assert len({
        r["risk_id"] for r in rows
    }) == len(rows)

    assert all(
        r["mitigation"] and r["verification_needed"]
        for r in rows
    )


def test_a04_readmes_link_to_artifacts():
    root = (
        ROOT / "README.md"
    ).read_text(encoding="utf-8")

    index = (
        ROOT / "docs/adr/README.md"
    ).read_text(encoding="utf-8")

    assert "08-platform-consumption-model.md" in root
    assert "A04.md" in root

    assert "ADR-006-capacity-admission.md" in index
    assert "ADR-007-consumption-accounting.md" in index
