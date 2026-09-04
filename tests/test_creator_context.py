from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


def test_creator_context_matches_public_schema() -> None:
    root = Path(__file__).resolve().parents[1]
    payload = json.loads(
        (root / "machine" / "creator-context.json").read_text(encoding="utf-8")
    )
    schema = json.loads(
        (root / "schemas" / "cmb.creator-context.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)


def test_creator_context_preserves_absolute_behavioral_boundary() -> None:
    payload = json.loads(
        Path("machine/creator-context.json").read_text(encoding="utf-8")
    )
    boundary = payload["behavioral_boundary"]

    assert boundary == {
        "catalog_is_creator": False,
        "index_is_identity": False,
        "profile_is_person": False,
        "context_is_identity": False,
        "prediction_is_destiny": False,
        "machine_may_define_person": False,
    }
    assert payload["authority"] == "HUMAN_FINAL"


def test_creator_context_keeps_evidence_lanes_distinct() -> None:
    payload = json.loads(
        Path("machine/creator-context.json").read_text(encoding="utf-8")
    )

    assert payload["lanes"]["symbolic"]["source_class"] == "DECLARED_CREATIVE_INFLUENCE"
    assert payload["lanes"]["technical"]["source_class"] == "ARTIFACT_EVIDENCE"
    assert (
        payload["lanes"]["intellectual"]["source_class"]
        == "DECLARED_AND_CITED_INTELLECTUAL_CONTEXT"
    )
    assert payload["lanes"]["symbolic"]["boundary"] == "SYMBOLISM_NOT_EMPIRICAL_EVIDENCE"
    assert payload["lanes"]["technical"]["boundary"] == "PROVENANCE_NOT_TOTAL_IDENTITY"
