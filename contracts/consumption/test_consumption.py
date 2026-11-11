"""A04 offline tests.

Run:
python -m unittest discover -s contracts/consumption -p test_consumption.py -v
"""

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "contracts/consumption"))

from evaluate import (  # noqa: E402
    EvaluationError,
    cpu_milli,
    digest,
    evaluate,
    memory_ki,
    read_json,
)

DECL = read_json(
    ROOT / "contracts/examples/valid-production.json"
)
SNAP = read_json(
    ROOT / "contracts/consumption/examples/production-snapshot.json"
)
HERE = ROOT / "contracts/consumption"


class ConsumptionTests(unittest.TestCase):

    def test_eligible_matches_committed_example(self):
        result = evaluate(DECL, SNAP)
        expected = read_json(
            HERE / "examples/eligible-decision.json"
        )

        self.assertEqual(result, expected)
        self.assertEqual(
            result["demand"]["cpuRequestMilli"], 500
        )
        self.assertEqual(
            result["demand"]["memoryRequestKi"], 524288
        )
        self.assertEqual(
            result["evaluationKind"], "advisory"
        )

    def test_denied_matches_committed_example(self):
        doc = copy.deepcopy(DECL)

        doc["workload"]["resources"].update(
            cpuRequest="3",
            cpuLimit="4"
        )

        result = evaluate(doc, SNAP)
        expected = read_json(
            HERE / "examples/denied-decision.json"
        )

        self.assertEqual(result, expected)
        self.assertEqual(
            result["reasons"],
            ["TEAM_CPU_EXCEEDED", "ENV_CPU_EXCEEDED"]
        )

    def test_exact_cpu_and_memory(self):
        self.assertEqual(cpu_milli("250m"), 250)
        self.assertEqual(cpu_milli("1.125"), 1125)
        self.assertEqual(memory_ki("1Gi"), 1048576)
        self.assertEqual(memory_ki("2Ti"), 2147483648)

        with self.assertRaises(EvaluationError):
            cpu_milli("1.0001")

    def test_team_memory_denial(self):
        snapshot = copy.deepcopy(SNAP)

        snapshot["team"]["entitlement"][
            "memoryRequestKi"
        ] = 1048576

        decision = evaluate(DECL, snapshot)

        self.assertIn(
            "TEAM_MEMORY_EXCEEDED",
            decision["reasons"]
        )

    def test_environment_capacity_denial(self):
        snapshot = copy.deepcopy(SNAP)

        snapshot["capacity"]["committed"][
            "cpuRequestMilli"
        ] = 9900

        decision = evaluate(DECL, snapshot)

        self.assertIn(
            "ENV_CPU_EXCEEDED",
            decision["reasons"]
        )

    def test_storage_not_replica_multiplied(self):
        doc = copy.deepcopy(DECL)

        doc["data"].update(
            stateful=True,
            storageGiB=10
        )

        decision = evaluate(doc, SNAP)

        self.assertEqual(
            decision["demand"]["storageGiB"], 10
        )

    def test_team_or_environment_mismatch_fails_closed(self):
        snapshot = copy.deepcopy(SNAP)
        snapshot["team"]["teamId"] = "another-team"

        with self.assertRaises(EvaluationError):
            evaluate(DECL, snapshot)

        snapshot = copy.deepcopy(SNAP)
        snapshot["environment"] = "staging"

        with self.assertRaises(EvaluationError):
            evaluate(DECL, snapshot)

    def test_overcommitted_and_invalid_snapshots_rejected(self):
        snapshot = copy.deepcopy(SNAP)

        snapshot["team"]["committed"][
            "cpuRequestMilli"
        ] = 5000

        with self.assertRaises(EvaluationError):
            evaluate(DECL, snapshot)

        snapshot = copy.deepcopy(SNAP)
        del snapshot["capacity"]["safetyHeadroom"]

        with self.assertRaises(EvaluationError):
            evaluate(DECL, snapshot)

    def test_cross_field_policy_and_schema_fails_closed(self):
        doc = copy.deepcopy(DECL)
        doc["workload"]["resources"]["cpuRequest"] = "2"

        with self.assertRaises(EvaluationError):
            evaluate(doc, SNAP)

        doc = copy.deepcopy(DECL)
        doc["data"].update(classification="restricted")
        doc["network"]["exposure"] = "public"

        with self.assertRaises(EvaluationError):
            evaluate(doc, SNAP)

        doc = copy.deepcopy(DECL)
        doc["approved"] = True

        with self.assertRaises(EvaluationError):
            evaluate(doc, SNAP)

    def test_digest_deterministic_and_revision_sensitive(self):
        normalized_copy = json.loads(
            json.dumps(DECL, sort_keys=True)
        )

        self.assertEqual(
            digest(DECL),
            digest(normalized_copy)
        )

        doc = copy.deepcopy(DECL)
        doc["metadata"]["revision"] += 1

        self.assertNotEqual(
            digest(DECL),
            digest(doc)
        )

    def test_example_schemas_and_denial_invariant(self):
        for name, filename in [
            ("snapshot", "capacity-snapshot.schema.json"),
            ("decision", "decision.schema.json")
        ]:
            schema = read_json(HERE / filename)
            Draft202012Validator.check_schema(schema)

            validator = Draft202012Validator(
                schema,
                format_checker=FormatChecker()
            )

            examples = (
                [SNAP]
                if name == "snapshot"
                else [
                    read_json(
                        HERE / "examples/eligible-decision.json"
                    ),
                    read_json(
                        HERE / "examples/denied-decision.json"
                    )
                ]
            )

            for value in examples:
                self.assertEqual(
                    list(validator.iter_errors(value)), []
                )

        bad = read_json(
            HERE / "examples/eligible-decision.json"
        )
        bad["reasons"] = ["TEAM_CPU_EXCEEDED"]

        schema = read_json(HERE / "decision.schema.json")

        self.assertTrue(
            list(
                Draft202012Validator(schema).iter_errors(bad)
            )
        )

    def test_storage_and_duplicate_key_rejections(self):
        snapshot = copy.deepcopy(SNAP)

        snapshot["team"]["entitlement"][
            "storageGiB"
        ] = 5

        doc = copy.deepcopy(DECL)
        doc["data"].update(
            stateful=True,
            storageGiB=10
        )

        self.assertIn(
            "TEAM_STORAGE_EXCEEDED",
            evaluate(doc, snapshot)["reasons"]
        )

        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text(
                '{"a":1,"a":2}',
                encoding="utf-8"
            )

            with self.assertRaises(EvaluationError):
                read_json(path)

    def test_cli_exit_codes(self):
        command = [
            sys.executable,
            str(HERE / "evaluate.py"),
            "--declaration",
            str(
                ROOT / "contracts/examples/valid-production.json"
            ),
            "--snapshot",
            str(
                HERE / "examples/production-snapshot.json"
            )
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        self.assertEqual(
            result.returncode, 0, result.stderr
        )

        self.assertEqual(
            json.loads(result.stdout)["status"],
            "eligible"
        )


if __name__ == "__main__":
    unittest.main()
