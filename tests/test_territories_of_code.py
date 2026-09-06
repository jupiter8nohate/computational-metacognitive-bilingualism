from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "cmb.territories-of-code.v1.schema.json"
RECORD_PATH = ROOT / "research" / "territories-of-code.v1.json"


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_territories_schema_is_valid_and_record_conforms() -> None:
    schema = _load_json(SCHEMA_PATH)
    record = _load_json(RECORD_PATH)

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(record)


def test_research_map_contains_exactly_ten_unique_territories() -> None:
    record = _load_json(RECORD_PATH)
    territories = record["territories"]
    assert isinstance(territories, list)
    assert len(territories) == 10

    ids = [territory["id"] for territory in territories]
    assert len(ids) == len(set(ids))


def test_priority_order_references_real_territories() -> None:
    record = _load_json(RECORD_PATH)
    territory_ids = {territory["id"] for territory in record["territories"]}
    assert set(record["priority_order"]) <= territory_ids


def test_map_refuses_unverified_novelty_claims() -> None:
    record = _load_json(RECORD_PATH)
    assert record["historical_claim"] == "candidate_and_emerging_territories_only"
    boundary = record["historical_claim_boundary"].lower()
    assert "does not claim" in boundary
    assert "prior-art" in boundary


def test_every_territory_has_evidence_and_safeguards() -> None:
    record = _load_json(RECORD_PATH)
    for territory in record["territories"]:
        assert len(territory["evidence_needed"]) >= 2
        assert len(territory["safeguards"]) >= 2
        assert len(territory["boundaries"]) >= 1
