
"""A03 contract unit tests: structural validation and illustrative policy checks.

Run: python -m unittest discover -s contracts/onboarding -p test_contract.py -v
"""

import copy
import json
import re
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]

SCHEMA = json.loads(
    (ROOT / "contracts/onboarding/schema.json").read_text(encoding="utf-8")
)
GOOD = json.loads(
    (ROOT / "contracts/examples/valid-production.json").read_text(encoding="utf-8")
)
BAD = json.loads(
    (ROOT / "contracts/examples/invalid-missing-ownership.json").read_text(encoding="utf-8")
)

VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def errors(document):
    return list(VALIDATOR.iter_errors(document))


def cpu_milli(qty):
    return int(qty[:-1]) if qty.endswith("m") else round(float(qty) * 1000)


def memory_bytes(qty):
    match = re.fullmatch(r"([1-9][0-9]*)(Ki|Mi|Gi|Ti)", qty)
    if not match:
        raise ValueError("invalid binary memory quantity")

    return int(match.group(1)) * 1024 ** {
        "Ki": 1,
        "Mi": 2,
        "Gi": 3,
        "Ti": 4
    }[match.group(2)]


def policy_errors(doc):
    """Illustrative cross-field checks; NOT authoritative admission authorization."""
    results = []
    res = doc["workload"]["resources"]

    if cpu_milli(res["cpuRequest"]) > cpu_milli(res["cpuLimit"]):
        results.append("cpu request exceeds limit")

    if memory_bytes(res["memoryRequest"]) > memory_bytes(res["memoryLimit"]):
        results.append("memory request exceeds limit")

    if (
        doc["data"]["classification"] == "restricted"
        and doc["network"]["exposure"] == "public"
    ):
        results.append("restricted data cannot request public exposure")

    return results


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Draft202012Validator.check_schema(SCHEMA)

    def test_valid_example(self):
        self.assertEqual(errors(GOOD), [])
        self.assertEqual(policy_errors(GOOD), [])

    def test_missing_owner(self):
        self.assertTrue(errors(BAD))

    def test_unknown_field_rejected(self):
        doc = copy.deepcopy(GOOD)
        doc["approved"] = True
        self.assertTrue(errors(doc))

    def test_invalid_email(self):
        doc = copy.deepcopy(GOOD)
        doc["owner"]["accountableEmail"] = "not-an-email"
        self.assertTrue(errors(doc))

    def test_nonstateful_storage_rejected(self):
        doc = copy.deepcopy(GOOD)
        doc["data"]["storageGiB"] = 10
        self.assertTrue(errors(doc))

    def test_stateful_requires_storage(self):
        doc = copy.deepcopy(GOOD)
        doc["data"]["stateful"] = True
        self.assertTrue(errors(doc))

    def test_critical_tier_requires_production(self):
        doc = copy.deepcopy(GOOD)
        doc["target"].update(
            serviceTier="critical",
            environment="staging"
        )
        self.assertTrue(errors(doc))

    def test_cpu_overcommit_detected_by_policy(self):
        doc = copy.deepcopy(GOOD)
        doc["workload"]["resources"].update(
            cpuRequest="2",
            cpuLimit="1"
        )
        self.assertEqual(errors(doc), [])
        self.assertIn("cpu request exceeds limit", policy_errors(doc))

    def test_memory_overcommit_detected_by_policy(self):
        doc = copy.deepcopy(GOOD)
        doc["workload"]["resources"].update(
            memoryRequest="2Gi",
            memoryLimit="1Gi"
        )
        self.assertEqual(errors(doc), [])
        self.assertIn("memory request exceeds limit", policy_errors(doc))

    def test_restricted_public_exposure_detected_by_policy(self):
        doc = copy.deepcopy(GOOD)
        doc["data"]["classification"] = "restricted"
        doc["network"]["exposure"] = "public"

        self.assertEqual(errors(doc), [])
        self.assertIn(
            "restricted data cannot request public exposure",
            policy_errors(doc)
        )

    def test_invalid_cpu_quantity(self):
        doc = copy.deepcopy(GOOD)
        doc["workload"]["resources"]["cpuRequest"] = "0m"
        self.assertTrue(errors(doc))

    def test_nested_unknown_field(self):
        doc = copy.deepcopy(GOOD)
        doc["owner"]["canCreateProduction"] = True
        self.assertTrue(errors(doc))


if __name__ == "__main__":
    unittest.main()
