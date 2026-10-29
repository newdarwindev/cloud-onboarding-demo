"""Tests use synthetic markers only; no live credentials or provider calls."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import ValidationError, check_schema, load_json, scan_patterns, validate


class DemoValidationTests(unittest.TestCase):
    def setUp(self):
        self.data = load_json(ROOT / "examples/status.mock.json")
        self.schema = load_json(ROOT / "schema/status.schema.json")

    def rejects(self, edit):
        edit(self.data)
        with self.assertRaises(ValidationError):
            validate(self.data, self.schema)

    def test_valid_demo(self):
        validate(self.data, self.schema)

    def test_mock_flag_required(self):
        self.rejects(lambda data: data.update(mock=False))

    def test_integer_is_not_boolean(self):
        self.rejects(lambda data: data.update(mock=1))

    def test_boolean_is_not_integer(self):
        self.rejects(lambda data: data.update(schema_version=True))

    def test_unknown_field_rejected(self):
        self.rejects(lambda data: data["providers"][0].update(account_id="MOCK"))

    def test_missing_field_rejected(self):
        self.rejects(lambda data: data.pop("notice"))

    def test_arbitrary_text_rejected(self):
        self.rejects(lambda data: data["providers"][0].update(reason="Harmless but non-allowlisted text"))

    def test_live_action_rejected(self):
        self.rejects(lambda data: data["providers"][0].update(live_actions_executed=True))

    def test_auto_approval_rejected(self):
        self.rejects(lambda data: data["providers"][0].update(automatic_approval=True))

    def test_duplicate_provider_rejected(self):
        self.rejects(lambda data: data["providers"].__setitem__(1, copy.deepcopy(data["providers"][0])))

    def test_missing_provider_rejected(self):
        self.rejects(lambda data: data["providers"].pop())

    def test_extra_provider_rejected(self):
        self.rejects(lambda data: data["providers"].append(copy.deepcopy(data["providers"][0])))

    def test_wrong_provider_source_rejected(self):
        self.rejects(lambda data: data["providers"][0].update(official_documentation=data["providers"][1]["official_documentation"]))

    def test_wrong_provider_id_rejected(self):
        self.rejects(lambda data: data["providers"][0].update(id="MOCK-AZURE"))

    def test_verification_without_mock_approval_rejected(self):
        self.rejects(lambda data: data["providers"][4].update(approval_reference="NOT_REQUESTED"))

    def test_verification_without_mock_human_rejected(self):
        self.rejects(lambda data: data["providers"][4].update(human_assignee="UNASSIGNED"))

    def test_premature_mock_pass_rejected(self):
        self.rejects(lambda data: data["providers"][0].update(verification_result="MOCK-PASS"))

    def test_unknown_schema_keyword_rejected(self):
        self.schema["properties"]["mock"]["newKeyword"] = True
        with self.assertRaises(ValidationError):
            validate(self.data, self.schema)

    def test_open_object_schema_rejected(self):
        self.schema["additionalProperties"] = True
        with self.assertRaises(ValidationError):
            check_schema(self.schema)

    def test_unconstrained_scalar_schema_rejected(self):
        with self.assertRaises(ValidationError):
            check_schema({"type": "string"})

    def test_unsupported_schema_type_rejected(self):
        with self.assertRaises(ValidationError):
            check_schema({"type": "number", "const": 1})

    def test_pattern_scanner_redacts_values(self):
        # Construct intentionally fake shapes at runtime, avoiding token-shaped literals in git.
        samples = ["AK" + "IA" + "A" * 16, "gh" + "p_" + "x" * 30,
                   "sk" + "-" + "x" * 30, "AI" + "za" + "x" * 35,
                   "-----BEGIN " + "PRIVATE KEY-----", "ey" + "Jabc.def.ghi",
                   "demo" + "@" + "example.invalid", "123456" + "789012",
                   "password" + "=" + "synthetic-value"]
        for sample in samples:
            with self.subTest(pattern_shape=sample[:2]):
                with self.assertRaises(ValidationError) as caught:
                    scan_patterns({"field": sample})
                self.assertNotIn(sample, str(caught.exception))
                self.assertIn("redacted", str(caught.exception))

    def test_secret_shaped_field_name_is_redacted(self):
        marker = "gh" + "p_" + "x" * 30
        with self.assertRaises(ValidationError) as caught:
            scan_patterns({marker: "MOCK"})
        self.assertNotIn(marker, str(caught.exception))

    def test_duplicate_json_field_rejected(self):
        self.assert_bad_json('{"mock":true,"mock":false}')

    def test_nonstandard_json_number_rejected(self):
        for source in ("NaN", "Infinity", "-Infinity"):
            self.assert_bad_json(source)

    def test_malformed_json_rejected(self):
        self.assert_bad_json('{"mock":')

    def test_input_size_limit(self):
        self.assert_bad_json(" " * 1_000_001)

    def assert_bad_json(self, source):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mock.json"
            path.write_text(source)
            with self.assertRaises(ValidationError):
                load_json(path)

    def test_cli_default_passes(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/validate.py")],
                                capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_cli_fails_closed_without_leaking_rejected_values(self):
        marker = "sk" + "-" + "x" * 30
        self.data["providers"][0]["reason"] = marker
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mock.json"
            path.write_text(json.dumps(self.data))
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate.py"), str(path)],
                                    capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(marker, result.stdout + result.stderr)
        self.assertIn("FAIL", result.stderr)


if __name__ == "__main__":
    unittest.main()
