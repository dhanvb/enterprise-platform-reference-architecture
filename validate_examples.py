import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

base = Path("contracts")

schema = json.loads(
    (base / "onboarding/schema.json").read_text(encoding="utf-8")
)

validator = Draft202012Validator(
    schema,
    format_checker=FormatChecker()
)

cases = [
    ("valid-staging.json", True),
    ("invalid-missing-owner.json", False),
]

for filename, expected_valid in cases:
    path = base / "examples" / filename

    document = json.loads(path.read_text(encoding="utf-8"))
    validation_errors = list(validator.iter_errors(document))

    actual_valid = not validation_errors

    passed = actual_valid == expected_valid

    print(f"{filename}: {'PASS' if passed else 'FAIL'}")

    for error in validation_errors:
        print(f"  Validation error: {error.message}")

    assert passed, f"Unexpected validation result: {filename}"
