"""A05 offline advisory evaluator; not a production authorization gate.

From repository root:
python contracts/delivery/evaluate.py --release contracts/delivery/examples/release.json --request contracts/delivery/examples/production-promotion.json --declaration contracts/examples/valid-production.json
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


class EvaluationError(ValueError):
    """Malformed input: reject assessment without issuing a decision."""


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate(document, schema_path):
    schema = read_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(document), key=lambda e: (list(map(str, e.path)), e.message))
    if errors:
        raise EvaluationError(f"schema validation failed: {errors[0].message}")


def onboarding_digest(declaration):
    """A04 Python demo encoding, NOT a standardized canonical JSON protocol."""
    binary = json.dumps(declaration, sort_keys=True, separators=(",", ":"),
                        ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(binary).hexdigest()


def evaluate(release, request, declaration):
    validate(release, HERE / "release.schema.json")
    validate(request, HERE / "promotion-request.schema.json")
    validate(declaration, ROOT / "contracts/onboarding/schema.json")

    reasons = []

    def deny_if(condition, reason):
        if condition and reason not in reasons:
            reasons.append(reason)

    deny_if(request["releaseId"] != release["releaseId"], "RELEASE_ID_MISMATCH")
    deny_if(request["applicationId"] != release["applicationId"] or
            request["applicationId"] != declaration["metadata"]["applicationId"],
            "APPLICATION_ID_MISMATCH")
    deny_if(request["artifactDigest"] != release["artifact"]["digest"],
            "ARTIFACT_DIGEST_MISMATCH")
    deny_if(not release["artifact"]["reference"].endswith("@" + release["artifact"]["digest"]),
            "ARTIFACT_REFERENCE_MISMATCH")
    deny_if(request["onboarding"]["revision"] != declaration["metadata"]["revision"],
            "ONBOARDING_REVISION_MISMATCH")
    deny_if(request["onboarding"]["sha256"] != onboarding_digest(declaration),
            "ONBOARDING_DIGEST_MISMATCH")
    deny_if(request["targetEnvironment"] != declaration["target"]["environment"],
            "TARGET_ENVIRONMENT_MISMATCH")

    evidence_by_type = {}
    for item in release["evidence"]:
        evidence_by_type.setdefault(item["type"], []).append(item)
        deny_if(item["subjectDigest"] != release["artifact"]["digest"],
                "EVIDENCE_DIGEST_MISMATCH")

    deny_if(any(len(items) > 1 for items in evidence_by_type.values()),
            "DUPLICATE_EVIDENCE_TYPE")

    required = {"development": ["unit-test"],
                "staging": ["unit-test", "integration-test"],
                "production": ["unit-test", "integration-test", "staging-verification"]}[request["targetEnvironment"]]
    missing_codes = {"unit-test": "MISSING_UNIT_TEST",
                     "integration-test": "MISSING_INTEGRATION_TEST",
                     "staging-verification": "MISSING_STAGING_EVIDENCE"}
    for item_type in required:
        claimed = evidence_by_type.get(item_type, [])
        deny_if(not claimed, missing_codes[item_type])
        deny_if(any(item["result"] != "passed" for item in claimed),
                "FAILED_REQUIRED_EVIDENCE")

    result = {
        "apiVersion": "platform.example.org/v1",
        "kind": "PromotionDecision",
        "evaluationKind": "advisory",
        "requestId": request["requestId"],
        "releaseId": request["releaseId"],
        "applicationId": request["applicationId"],
        "targetEnvironment": request["targetEnvironment"],
        "artifactDigest": request["artifactDigest"],
        "configurationRevision": request["configurationRevision"],
        "onboardingSha256": request["onboarding"]["sha256"],
        "policyVersion": request["policyVersion"],
        "outcome": "denied" if reasons else "eligible",
        "reasons": reasons,
    }
    validate(result, HERE / "decision.schema.json")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--declaration", required=True)
    args = parser.parse_args()
    try:
        decision = evaluate(read_json(args.release), read_json(args.request),
                            read_json(args.declaration))
    except (EvaluationError, OSError, ValueError) as exc:
        print(f"rejected: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(decision, indent=2))
    return 0 if decision["outcome"] == "eligible" else 3


if __name__ == "__main__":
    sys.exit(main())
