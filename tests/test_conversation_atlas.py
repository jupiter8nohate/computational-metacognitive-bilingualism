from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
ATLAS_PATH = ROOT / "library" / "cmb-conversation-atlas.v1.json"
SCHEMA_PATH = ROOT / "schemas" / "cmb.conversation-atlas.v1.schema.json"


def _load() -> tuple[dict[str, object], dict[str, object]]:
    atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return atlas, schema


def test_conversation_atlas_matches_strict_public_schema() -> None:
    atlas, schema = _load()
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(atlas)


def test_conversation_atlas_preserves_canonical_name_and_boundaries() -> None:
    atlas, _ = _load()

    assert atlas["schema"] == "cmb.conversation-atlas.v1"
    assert atlas["naming"]["canonical_public_language_name"] == "Err ⃝or⃟⃤ GLITCHOLOGY"
    assert atlas["naming"]["implementation_layer"] == "GLITCH-8 / CMB-G8"

    invariants = set(atlas["invariants"])
    assert "PATTERN != PROOF" in invariants
    assert "PROFILE != PERSON" in invariants
    assert "MODEL != MIND" in invariants
    assert "HUMAN_AGENCY > MACHINE_AUTHORITY" in invariants

    boundaries = set(atlas["translation_contract"]["required_boundaries"])
    assert "PROVENANCE != CONSCIOUSNESS" in boundaries
    assert "CREATIVE_SIGNATURE != COMPLETE_PERSON" in boundaries


def test_conversation_atlas_ids_are_unique() -> None:
    atlas, _ = _load()
    concept_ids = [item["id"] for item in atlas["concepts"]]
    sequence_ids = [item["id"] for item in atlas["symbolic_sequences"]]

    assert len(concept_ids) == len(set(concept_ids))
    assert len(sequence_ids) == len(set(sequence_ids))


def test_conversation_atlas_schema_rejects_semantic_drift() -> None:
    atlas, schema = _load()
    validator = Draft202012Validator(schema)

    mutated = copy.deepcopy(atlas)
    mutated["translation_contract"]["semantics_must_not_drift"] = False
    with pytest.raises(ValidationError):
        validator.validate(mutated)

    mutated = copy.deepcopy(atlas)
    mutated["evidence_boundaries"]["hash"] = "proof_of_authorship"
    with pytest.raises(ValidationError):
        validator.validate(mutated)

    mutated = copy.deepcopy(atlas)
    mutated["naming"]["canonical_public_language_name"] = "GLITCHOLOGY"
    with pytest.raises(ValidationError):
        validator.validate(mutated)


def test_sovereign_retry_loop_is_preserved() -> None:
    atlas, _ = _load()
    sequence = next(
        item for item in atlas["symbolic_sequences"]
        if item["id"] == "GLITCH://404_SOVEREIGN_RETRY_LOOP"
    )

    assert sequence["semantic_flow"][-1] == "RECOVERY"
    assert "404 != NONEXISTENCE" in sequence["invariants"]
    assert "The system failed to understand the signal" in sequence["plain_language"]
