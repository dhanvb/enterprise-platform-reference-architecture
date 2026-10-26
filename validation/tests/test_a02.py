
"""A02: Validate architecture evidence consistency.

Uses Python standard library only.
Does not test or deploy any platform products.
"""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs" / "architecture"
DEC = ROOT / "docs" / "decisions"


def read_csv(filename, required_columns):
    path = DEC / filename

    with path.open(encoding="utf-8-sig", newline="") as f:
        lines = (line for line in f if line.strip())
        reader = csv.DictReader(lines)

        if not reader.fieldnames:
            raise AssertionError(f"{filename}: missing header")

        reader.fieldnames = [x.strip() for x in reader.fieldnames]

        missing = set(required_columns) - set(reader.fieldnames)
        assert not missing, (
            f"{filename}: missing columns {sorted(missing)}"
        )

        rows = list(reader)

    assert rows, f"{filename}: no records"
    return rows


def test_traceability():
    requirements = (
        ARCH / "05-platform-requirements.md"
    ).read_text(encoding="utf-8")

    capabilities = (
        ARCH / "04-capability-catalog.md"
    ).read_text(encoding="utf-8")

    req_list = re.findall(
        r"^### (REQ-[FNSO]\d{2}):",
        requirements,
        flags=re.MULTILINE,
    )

    cap_list = re.findall(
        r"^## \d+\. (CAP-\d{2}):",
        capabilities,
        flags=re.MULTILINE,
    )

    assert len(req_list) == len(set(req_list))
    assert len(cap_list) == len(set(cap_list))
    assert len(req_list) == 16
    assert len(cap_list) == 8

    rows = read_csv(
        "capability-traceability.csv",
        [
            "requirement_id",
            "requirement_category",
            "priority",
            "capability_ids",
            "verification_method",
        ],
    )

    mapped = [r["requirement_id"] for r in rows]

    assert len(mapped) == len(set(mapped)), (
        "Duplicate requirement mappings"
    )

    assert set(mapped) == set(req_list), (
        "Requirements and mappings do not match"
    )

    for row in rows:
        assert row["priority"] in {"Must", "Should"}
        assert row["verification_method"].strip()

        for cap in row["capability_ids"].split(";"):
            assert cap in cap_list, (
                f"Unknown capability {cap}"
            )

    print(
        f"PASS: {len(req_list)} requirements mapped "
        f"to {len(cap_list)} capabilities"
    )


CRITERIA = {
    "Security and governance": 25,
    "Operational maintainability": 20,
    "Functional capability": 20,
    "Reliability and lifecycle": 15,
    "Total cost of ownership": 10,
    "Organizational skills": 10,
}


def test_scorecard():
    rows = read_csv(
        "technology-scorecard.csv",
        [
            "category",
            "candidate",
            "criterion",
            "weight",
            "gate_status",
            "score",
            "evidence_reference",
            "assessment_status",
        ],
    )

    seen = set()
    grouped = {}

    for row in rows:
        key = (
            row["category"],
            row["candidate"],
            row["criterion"],
        )
        assert key not in seen, f"Duplicate scorecard row {key}"
        seen.add(key)

        criterion = row["criterion"]
        assert criterion in CRITERIA
        assert int(row["weight"]) == CRITERIA[criterion]

        group = (row["category"], row["candidate"])
        grouped.setdefault(group, set()).add(criterion)

        assert row["gate_status"] in {
            "PASS", "FAIL", "UNKNOWN"
        }

        if row["assessment_status"] == "NOT_ASSESSED":
            assert row["gate_status"] == "UNKNOWN"
            assert not row["score"].strip()
            assert not row["evidence_reference"].strip()
        else:
            assert row["assessment_status"] == "ASSESSED"
            assert row["gate_status"] in {"PASS", "FAIL"}
            assert row["score"].strip()
            assert 1 <= int(row["score"]) <= 5
            assert row["evidence_reference"].strip()

    assert rows
    complete = sum(
        criteria == set(CRITERIA)
        for criteria in grouped.values()
    )

    print(
        f"PASS: {len(rows)} candidate scorecard rows checked"
    )
    print(
        f"INFO: {complete} candidates have "
        "all criteria represented"
    )
    print("INFO: Product assessments remain unverified")


def weighted_score(weights, scores):
    assert set(weights) == set(scores)
    assert sum(weights.values()) == 100

    return sum(
        weights[k] * scores[k]
        for k in weights
    ) / 100


def test_worked_example():
    a = {
        "Security and governance": 3,
        "Operational maintainability": 3,
        "Functional capability": 4,
        "Reliability and lifecycle": 3,
        "Total cost of ownership": 5,
        "Organizational skills": 4,
    }

    b = {
        "Security and governance": 4,
        "Operational maintainability": 4,
        "Functional capability": 4,
        "Reliability and lifecycle": 4,
        "Total cost of ownership": 2,
        "Organizational skills": 3,
    }

    initial_a = weighted_score(CRITERIA, a)
    initial_b = weighted_score(CRITERIA, b)

    sensitivity_weights = {
        "Security and governance": 15,
        "Operational maintainability": 15,
        "Functional capability": 15,
        "Reliability and lifecycle": 10,
        "Total cost of ownership": 35,
        "Organizational skills": 10,
    }

    revised_a = weighted_score(sensitivity_weights, a)
    revised_b = weighted_score(sensitivity_weights, b)

    assert round(initial_a, 2) == 3.50
    assert round(initial_b, 2) == 3.70
    assert round(revised_a, 2) == 3.95
    assert round(revised_b, 2) == 3.20

    assert initial_b > initial_a
    assert revised_a > revised_b

    print("PASS: hypothetical weighted calculations")
    print("PASS: decision ranking reverses under new weights")


def test_risk_register():
    rows = read_csv(
        "risk-register.csv",
        [
            "risk_id",
            "description",
            "impact",
            "likelihood",
            "status",
            "mitigation",
            "owner_role",
            "related_requirements",
        ],
    )

    requirements = (
        ARCH / "05-platform-requirements.md"
    ).read_text(encoding="utf-8")

    req_ids = set(re.findall(
        r"^### (REQ-[FNSO]\d{2}):",
        requirements,
        flags=re.MULTILINE,
    ))

    risk_ids = [r["risk_id"] for r in rows]
    assert len(risk_ids) == len(set(risk_ids))

    for row in rows:
        assert row["description"].strip()
        assert row["mitigation"].strip()
        assert row["owner_role"].strip()
        assert row["impact"] in {
            "Low", "Medium", "High", "Critical"
        }
        assert row["likelihood"] in {
            "Low", "Medium", "High"
        }
        assert row["status"] in {
            "Open", "Mitigated", "Accepted", "Closed"
        }

        for req in row["related_requirements"].split(";"):
            assert req in req_ids, (
                f"Unknown requirement {req}"
            )

    print(f"PASS: {len(rows)} risk records validated")


def main():
    test_traceability()
    test_scorecard()
    test_worked_example()
    test_risk_register()

    print("PASS: A02 architecture evidence validation")
    print("NOTE: This is not product or runtime verification")


if __name__ == "__main__":
    main()
