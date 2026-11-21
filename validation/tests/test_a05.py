"""A05 repository structure/traceability checks, not runtime proof."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "docs/architecture/09-enterprise-software-delivery.md",
    "docs/hld/HLD-004-software-delivery.md",
    "docs/adr/ADR-008-release-artifact-identity.md",
    "docs/adr/ADR-009-promotion-and-authorization.md",
    "docs/assets/diagrams/src/06-release-promotion.dot",
    "docs/assets/diagrams/svg/06-release-promotion.svg",
    "docs/decisions/delivery-traceability.csv",
    "docs/decisions/delivery-risk-register.csv",
    "contracts/delivery/README.md",
    "contracts/delivery/release.schema.json",
    "contracts/delivery/promotion-request.schema.json",
    "contracts/delivery/decision.schema.json",
    "contracts/delivery/evaluate.py",
    "contracts/delivery/test_delivery.py",
    "contracts/delivery/examples/release.json",
    "contracts/delivery/examples/production-promotion.json",
    "contracts/delivery/examples/eligible-decision.json",
    "contracts/delivery/examples/denied-decision.json",
    "validation/reports/A05-validation.md",
    "evidence/A05.md",
    ".github/workflows/a05-validation.yml",
]


def test_required_a05_files():
    for name in REQUIRED:
        path = ROOT / name
        assert path.is_file() and path.stat().st_size > 20, name


def test_requirement_traceability():
    arch = (ROOT / REQUIRED[0]).read_text(encoding="utf-8")
    with (ROOT / "docs/decisions/delivery-traceability.csv").open(newline="", encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    assert {row["requirement_id"] for row in records} == {f"A05-R{i:02d}" for i in range(1, 15)}
    assert len(records) == 14
    allowed = {"Design", "Pending static verification", "Pending integration", "Pending runtime"}
    for row in records:
        assert row["requirement_id"] in arch
        assert row["verification_method"] and row["evidence_status"] in allowed
        for filename in row["evidence_path"].split(";"):
            assert (ROOT / filename).is_file(), filename


def test_risk_register():
    with (ROOT / "docs/decisions/delivery-risk-register.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 10
    assert len({row["risk_id"] for row in rows}) == len(rows)
    assert all(row["mitigation"] and row["verification_needed"] for row in rows)


def test_integration_indexes():
    root = (ROOT / "README.md").read_text(encoding="utf-8")
    adr = (ROOT / "docs/adr/README.md").read_text(encoding="utf-8")
    assert "09-enterprise-software-delivery.md" in root
    assert "evidence/A05.md" in root
    assert "ADR-008-release-artifact-identity.md" in adr
    assert "ADR-009-promotion-and-authorization.md" in adr


def test_evidence_boundaries():
    index = (ROOT / "evidence/A05.md").read_text(encoding="utf-8")
    report = (ROOT / "validation/reports/A05-validation.md").read_text(encoding="utf-8")
    assert "not production" in index.lower()
    assert "not production" in report.lower()
