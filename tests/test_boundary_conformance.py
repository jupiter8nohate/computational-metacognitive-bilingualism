from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from cmb_provenance import BoundaryContext, evaluate_boundary

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "conformance" / "boundary.v1.cases.json"
EVENT_SCHEMA = ROOT / "schemas" / "cmb.boundary-event.v1.schema.json"


def _normalized_decision(context: BoundaryContext) -> dict[str, object]:
    decision = evaluate_boundary(context)
    return {
        "allowed": decision.allowed,
        "authority": decision.authority,
        "violations": [
            {"code": item.code.value, "invariant": item.invariant}
            for item in decision.violations
        ],
    }


def test_python_reference_engine_matches_shared_conformance_cases() -> None:
    fixture = json.loads(CASES.read_text(encoding="utf-8"))
    schema = json.loads(EVENT_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    assert fixture["schema_version"] == "cmb.boundary-conformance.v1"

    ids: list[str] = []
    for case in fixture["cases"]:
        ids.append(case["id"])
        event = case["event"]
        validator.validate(event)

        context_payload = dict(event)
        assert context_payload.pop("schema_version") == "cmb.boundary-event.v1"
        context = BoundaryContext(**context_payload)

        assert _normalized_decision(context) == case["expected"], case["id"]

    assert len(ids) == len(set(ids))
