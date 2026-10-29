#!/usr/bin/env python3
"""Offline, fail-closed validator for a deliberately narrow synthetic JSON format.

This implements only the documented schema keyword subset below, not all JSON Schema.
It never contacts providers, reads environment variables, or prints rejected values.
"""

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
KEYWORDS = {
    "$schema", "title", "description", "type", "const", "enum", "required",
    "properties", "additionalProperties", "items", "minItems", "maxItems",
}
TYPES = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}
PROVIDERS = {
    "AWS": ("MOCK-AWS", "https://docs.aws.amazon.com/"),
    "Azure": ("MOCK-AZURE", "https://learn.microsoft.com/en-us/azure/"),
    "Google Cloud": ("MOCK-GOOGLE-CLOUD", "https://docs.cloud.google.com/docs"),
    "Cloudflare": ("MOCK-CLOUDFLARE", "https://developers.cloudflare.com/"),
    "LLM providers": ("MOCK-LLM", "MOCK: Provider selection pending"),
}
LIFECYCLE = {
    ("research", "planned", "NOT_REQUESTED", "UNASSIGNED", "NOT_RUN"),
    ("owner_approval", "blocked", "NOT_REQUESTED", "UNASSIGNED", "NOT_RUN"),
    ("human_security_handoff", "blocked", "MOCK-APPROVAL-REFERENCE", "MOCK-VERIFIED-HUMAN", "NOT_RUN"),
    ("authorized_verification", "ready_for_mock_review", "MOCK-APPROVAL-REFERENCE", "MOCK-VERIFIED-HUMAN", "NOT_RUN"),
    ("authorized_verification", "verified_mock", "MOCK-APPROVAL-REFERENCE", "MOCK-VERIFIED-HUMAN", "MOCK-PASS"),
}
PATTERNS = {
    "cloud access key shape": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "GitHub token shape": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "API secret shape": re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    "Google API key shape": re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b"),
    "private key marker": re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"),
    "JWT shape": re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
    "email shape": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "account number shape": re.compile(r"\b\d{12}\b"),
    "credential assignment shape": re.compile(r"(?i)(?:password|secret|api[_-]?key|access[_-]?token)\s*[=:]\s*\S+"),
}


class ValidationError(ValueError):
    """Safe-to-print error: never include rejected input values."""


def reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("JSON contains a duplicate field")
        result[key] = value
    return result


def reject_constant(_value):
    raise ValidationError("JSON contains a nonstandard numeric constant")


def load_json(path):
    # Bound the input and avoid returning raw decoder errors or source excerpts.
    try:
        with Path(path).open("rb") as source:
            raw = source.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValidationError("JSON input exceeds the 1 MB limit")
        return json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicates,
                          parse_constant=reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError):
        raise ValidationError("JSON input is unreadable, malformed, or too deeply nested") from None


def check_schema(schema):
    if type(schema) is not dict or set(schema) - KEYWORDS:
        raise ValidationError("Schema has an unsupported keyword or shape")
    if schema.get("type") not in TYPES:
        raise ValidationError("Schema has an unsupported or missing type")
    if "enum" in schema and (type(schema["enum"]) is not list or not schema["enum"]):
        raise ValidationError("Schema enum must be a nonempty list")
    if schema["type"] == "object":
        if schema.get("additionalProperties") is not False:
            raise ValidationError("Schema objects must reject unknown fields")
        props, required = schema.get("properties"), schema.get("required")
        if type(props) is not dict or type(required) is not list:
            raise ValidationError("Schema object fields must be explicitly declared")
        if any(type(key) is not str for key in required) or set(required) != set(props):
            raise ValidationError("Schema object must require exactly its declared fields")
        for child in props.values():
            check_schema(child)
    elif schema["type"] == "array":
        if "items" not in schema:
            raise ValidationError("Schema array requires an item schema")
        for limit in ("minItems", "maxItems"):
            if type(schema.get(limit)) is not int or schema[limit] < 0:
                raise ValidationError("Schema arrays require nonnegative integer bounds")
        if schema["minItems"] > schema["maxItems"]:
            raise ValidationError("Schema array bounds are inconsistent")
        check_schema(schema["items"])
    else:
        if "const" not in schema and "enum" not in schema:
            raise ValidationError("Schema scalars must be allowlisted")
    if schema["type"] != "object" and any(k in schema for k in ("properties", "required", "additionalProperties")):
        raise ValidationError("Schema object keywords used on another type")
    if schema["type"] != "array" and any(k in schema for k in ("items", "minItems", "maxItems")):
        raise ValidationError("Schema array keywords used on another type")


def validate_shape(value, schema, path="$ mock data"):
    if type(value) is not TYPES[schema["type"]]:
        raise ValidationError(f"{path}: wrong value type")
    if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
        raise ValidationError(f"{path}: value is not the required mock constant")
    if "enum" in schema and not any(type(value) is type(item) and value == item for item in schema["enum"]):
        raise ValidationError(f"{path}: value is not an allowed mock option")
    if type(value) is dict:
        if set(value) != set(schema["properties"]):
            raise ValidationError(f"{path}: missing or unknown field")
        for key, child in schema["properties"].items():
            validate_shape(value[key], child, f"{path}.{key}")
    elif type(value) is list:
        if not schema["minItems"] <= len(value) <= schema["maxItems"]:
            raise ValidationError(f"{path}: item count outside permitted bounds")
        for index, item in enumerate(value):
            validate_shape(item, schema["items"], f"{path}[{index}]")


def scan_patterns(value, path="$ mock data"):
    if type(value) is dict:
        for index, (key, child) in enumerate(value.items()):
            # Never interpolate an input key: it may itself contain a secret.
            scan_patterns(key, f"{path}.field[{index}].name")
            scan_patterns(child, f"{path}.field[{index}].value")
    elif type(value) is list:
        for index, child in enumerate(value):
            scan_patterns(child, f"{path}[{index}]")
    elif type(value) is str:
        for name, pattern in PATTERNS.items():
            if pattern.search(value):
                raise ValidationError(f"{path}: rejected {name}; value redacted")


def validate(data, schema):
    check_schema(schema)
    scan_patterns(data)
    validate_shape(data, schema)
    records = data["providers"]
    if len({record["provider"] for record in records}) != len(PROVIDERS):
        raise ValidationError("Mock provider categories must appear exactly once")
    for index, record in enumerate(records):
        expected_id, expected_url = PROVIDERS[record["provider"]]
        if (record["id"], record["official_documentation"]) != (expected_id, expected_url):
            raise ValidationError(f"Mock provider record {index}: category/id/source mismatch")
        lifecycle = tuple(record[key] for key in
                          ("phase", "status", "approval_reference", "human_assignee", "verification_result"))
        if lifecycle not in LIFECYCLE:
            raise ValidationError(f"Mock provider record {index}: inconsistent lifecycle gates")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", nargs="?", type=Path, default=ROOT / "examples/status.mock.json")
    args = parser.parse_args()
    try:
        validate(load_json(args.data), load_json(ROOT / "schema/status.schema.json"))
    except (ValidationError, RecursionError) as error:
        message = str(error) if isinstance(error, ValidationError) else "Input nesting exceeds supported depth"
        print(f"FAIL: {message}", file=sys.stderr)
        return 1
    print("PASS: 5 synthetic provider records; schema, lifecycle, and pattern checks passed. No live actions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
