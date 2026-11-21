"""A05 offline contract and policy tests (no production controls)."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from evaluate import EvaluationError, evaluate, onboarding_digest, read_json  # noqa: E402

RELEASE = read_json(HERE / "examples/release.json")
REQUEST = read_json(HERE / "examples/production-promotion.json")
DECLARATION = read_json(ROOT / "contracts/examples/valid-production.json")


class DeliveryTests(unittest.TestCase):
    def test_eligible_matches_fixture(self):
        self.assertEqual(evaluate(RELEASE, REQUEST, DECLARATION),
                         read_json(HERE / "examples/eligible-decision.json"))

    def test_denied_matches_fixture(self):
        request = copy.deepcopy(REQUEST)
        request["artifactDigest"] = "sha256:" + "d" * 64
        self.assertEqual(evaluate(RELEASE, request, DECLARATION),
                         read_json(HERE / "examples/denied-decision.json"))

    def test_schemas_and_fixture_validation(self):
        pairs = [
            ("release.schema.json", [RELEASE]),
            ("promotion-request.schema.json", [REQUEST]),
            ("decision.schema.json", [read_json(HERE / "examples/eligible-decision.json"),
                                      read_json(HERE / "examples/denied-decision.json")]),
        ]
        for filename, documents in pairs:
            schema = read_json(HERE / filename)
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema, format_checker=FormatChecker())
            for document in documents:
                self.assertFalse(list(validator.iter_errors(document)), filename)

    def test_mutable_or_mismatched_artifact_rejected_or_denied(self):
        release = copy.deepcopy(RELEASE)
        release["artifact"]["reference"] = "registry.example.org/orders-api:latest"
        with self.assertRaises(EvaluationError):
            evaluate(release, REQUEST, DECLARATION)
        release = copy.deepcopy(RELEASE)
        release["artifact"]["reference"] = "registry.example.org/orders-api@sha256:" + "d" * 64
        self.assertIn("ARTIFACT_REFERENCE_MISMATCH",
                      evaluate(release, REQUEST, DECLARATION)["reasons"])

    def test_release_and_application_mismatch(self):
        request = copy.deepcopy(REQUEST)
        request["releaseId"] = "different-release"
        request["applicationId"] = "other-api"
        reasons = evaluate(RELEASE, request, DECLARATION)["reasons"]
        self.assertIn("RELEASE_ID_MISMATCH", reasons)
        self.assertIn("APPLICATION_ID_MISMATCH", reasons)

    def test_onboarding_revision_and_digest_binding(self):
        request = copy.deepcopy(REQUEST)
        request["onboarding"]["revision"] = 2
        self.assertIn("ONBOARDING_REVISION_MISMATCH",
                      evaluate(RELEASE, request, DECLARATION)["reasons"])
        declaration = copy.deepcopy(DECLARATION)
        declaration["metadata"]["displayName"] = "Renamed Orders API"
        self.assertIn("ONBOARDING_DIGEST_MISMATCH",
                      evaluate(RELEASE, REQUEST, declaration)["reasons"])

    def test_declaration_environment_binding(self):
        declaration = copy.deepcopy(DECLARATION)
        declaration["target"]["environment"] = "staging"
        request = copy.deepcopy(REQUEST)
        request["onboarding"]["sha256"] = onboarding_digest(declaration)
        self.assertIn("TARGET_ENVIRONMENT_MISMATCH",
                      evaluate(RELEASE, request, declaration)["reasons"])

    def test_missing_evidence_by_environment(self):
        release = copy.deepcopy(RELEASE)
        release["evidence"] = release["evidence"][:1]
        reasons = evaluate(release, REQUEST, DECLARATION)["reasons"]
        self.assertIn("MISSING_INTEGRATION_TEST", reasons)
        self.assertIn("MISSING_STAGING_EVIDENCE", reasons)

    def test_failed_and_wrong_subject_evidence(self):
        release = copy.deepcopy(RELEASE)
        release["evidence"][0]["result"] = "failed"
        release["evidence"][1]["subjectDigest"] = "sha256:" + "d" * 64
        reasons = evaluate(release, REQUEST, DECLARATION)["reasons"]
        self.assertIn("FAILED_REQUIRED_EVIDENCE", reasons)
        self.assertIn("EVIDENCE_DIGEST_MISMATCH", reasons)

    def test_duplicate_evidence_type(self):
        release = copy.deepcopy(RELEASE)
        release["evidence"].append(copy.deepcopy(release["evidence"][0]))
        self.assertIn("DUPLICATE_EVIDENCE_TYPE",
                      evaluate(release, REQUEST, DECLARATION)["reasons"])

    def test_staging_policy(self):
        declaration = copy.deepcopy(DECLARATION)
        declaration["target"]["environment"] = "staging"
        request = copy.deepcopy(REQUEST)
        request["targetEnvironment"] = "staging"
        request["onboarding"]["sha256"] = onboarding_digest(declaration)
        release = copy.deepcopy(RELEASE)
        release["evidence"] = release["evidence"][:2]
        self.assertEqual(evaluate(release, request, declaration)["outcome"], "eligible")

    def test_development_policy(self):
        declaration = copy.deepcopy(DECLARATION)
        declaration["target"]["environment"] = "development"
        request = copy.deepcopy(REQUEST)
        request["targetEnvironment"] = "development"
        request["onboarding"]["sha256"] = onboarding_digest(declaration)
        release = copy.deepcopy(RELEASE)
        release["evidence"] = release["evidence"][:1]
        self.assertEqual(evaluate(release, request, declaration)["outcome"], "eligible")

    def test_no_applicant_approval_field(self):
        request = copy.deepcopy(REQUEST)
        request["approved"] = True
        with self.assertRaises(EvaluationError):
            evaluate(RELEASE, request, DECLARATION)

    def test_missing_builder_or_invalid_policy_rejected(self):
        release = copy.deepcopy(RELEASE)
        del release["build"]["provenanceRef"]
        with self.assertRaises(EvaluationError):
            evaluate(release, REQUEST, DECLARATION)
        request = copy.deepcopy(REQUEST)
        request["policyVersion"] = "unknown-policy"
        with self.assertRaises(EvaluationError):
            evaluate(RELEASE, request, DECLARATION)

    def test_configuration_revision_is_recorded_not_approved(self):
        request = copy.deepcopy(REQUEST)
        request["configurationRevision"] = "f" * 40
        decision = evaluate(RELEASE, request, DECLARATION)
        self.assertEqual(decision["configurationRevision"], "f" * 40)
        self.assertEqual(decision["evaluationKind"], "advisory")

    def test_cli_exit_codes(self):
        base = [sys.executable, str(HERE / "evaluate.py"),
                "--release", str(HERE / "examples/release.json"),
                "--declaration", str(ROOT / "contracts/examples/valid-production.json")]
        result = subprocess.run(base + ["--request", str(HERE / "examples/production-promotion.json")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["outcome"], "eligible")
        with tempfile.TemporaryDirectory() as directory:
            req_file = Path(directory) / "request.json"
            changed = copy.deepcopy(REQUEST)
            changed["artifactDigest"] = "sha256:" + "d" * 64
            req_file.write_text(json.dumps(changed), encoding="utf-8")
            result = subprocess.run(base + ["--request", str(req_file)],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 3, result.stderr)
            changed["approved"] = True
            req_file.write_text(json.dumps(changed), encoding="utf-8")
            result = subprocess.run(base + ["--request", str(req_file)],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
