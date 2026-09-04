from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


def load_registry() -> dict[str, object]:
    return json.loads(Path("machine/use-cases.json").read_text(encoding="utf-8"))


def test_use_case_registry_matches_schema() -> None:
    registry = load_registry()
    schema = json.loads(
        Path("schemas/cmb.use-cases.v1.schema.json").read_text(encoding="utf-8")
    )

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(registry)


def test_current_capability_claims_are_only_deployable_now() -> None:
    registry = load_registry()

    for case in registry["use_cases"]:
        if case["claims_current_capability"]:
            assert case["category"] == "DEPLOYABLE_NOW"


def test_future_cases_never_claim_current_capability() -> None:
    registry = load_registry()

    future = [case for case in registry["use_cases"] if case["year"] > 2026]
    assert future
    assert all(case["category"] == "SPECULATIVE_FUTURE" for case in future)
    assert all(case["claims_current_capability"] is False for case in future)


def test_use_case_registry_preserves_human_final_authority() -> None:
    registry = load_registry()

    assert registry["decision_rule"]["authority"] == "HUMAN_FINAL"
    assert registry["categories"] == [
        "DEPLOYABLE_NOW",
        "REQUIRES_INTEGRATION",
        "SPECULATIVE_FUTURE",
    ]
