from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "library" / "creator-provenance.json"
SCHEMA_PATH = ROOT / "schemas" / "cmb.creator-provenance.v1.schema.json"


def _load_registry() -> dict[str, object]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_creator_provenance_matches_public_schema() -> None:
    registry = _load_registry()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(registry)


def test_creator_provenance_preserves_evidence_boundaries() -> None:
    registry = _load_registry()
    boundaries = registry["epistemic_boundaries"]

    assert boundaries["genealogy_is_metaphysical_proof"] is False
    assert boundaries["symbolism_is_biological_fact"] is False
    assert boundaries["symbolism_is_scientific_evidence"] is False
    assert boundaries["third_party_reference_implies_affiliation"] is False
    assert boundaries["pattern_is_proof"] is False
    assert boundaries["human_agency_over_machine_authority"] is True


def test_creator_provenance_genealogy_is_bounded_and_unverified() -> None:
    registry = _load_registry()
    genealogy = registry["evidence_model"]["genealogy_source"]

    assert genealogy["source_type"] == "creator_supplied_family_tree"
    assert genealogy["status"] == "creator_documented_not_independently_verified"
    assert genealogy["independent_verification"] is False
    assert genealogy["public_source_material_in_repository"] is False
    assert genealogy["living_relative_details_in_public_registry"] is False


def test_creator_provenance_privacy_fails_closed() -> None:
    registry = _load_registry()
    privacy = registry["privacy_policy"]

    assert privacy["publish_raw_family_tree"] is False
    assert privacy["publish_invite_tokens"] is False
    assert privacy["publish_living_relative_details"] is False
    assert privacy["retain_only_minimum_public_claim"] is True

    rendered = REGISTRY_PATH.read_text(encoding="utf-8")
    assert "inviteId" not in rendered
    assert "ancestry.com/family-tree" not in rendered.lower()


def test_creator_provenance_symbolic_categories_are_explicit() -> None:
    registry = _load_registry()
    symbolic = {
        item["reference"]: item["classification"]
        for item in registry["symbolic_lineage"]
    }

    assert symbolic["Yahweh"] == "religious_symbolic_reference"
    assert symbolic["Thoth"] == "mythological_symbolic_reference"
    assert symbolic["Pokemon / Pokedex"] == "third_party_cultural_reference"
    assert symbolic["MissingNo"] == "third_party_game_glitch_reference"
    assert symbolic["6 / 66 / 666"] == "author_defined_symbolic_operator"
