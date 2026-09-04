from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from cmb_provenance.release import CANONICAL_PUBLIC_ARTIFACTS

CATALOG_SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "cmb.library.catalog.v1.schema.json"


def _load_catalog() -> tuple[Path, dict[str, object]]:
    repository_root = Path(__file__).resolve().parents[1]
    path = repository_root / "library" / "catalog.json"
    return repository_root, json.loads(path.read_text(encoding="utf-8"))


def test_library_catalog_has_stable_schema_and_invariants() -> None:
    _, catalog = _load_catalog()

    assert catalog["schema_version"] == "cmb.library.catalog.v1"
    assert catalog["framework"] == "Computational Metacognitive Bilingualism"

    invariants = set(catalog["invariants"])
    assert "PATTERN != PROOF" in invariants
    assert "PROFILE != PERSON" in invariants
    assert "MODEL != MIND" in invariants
    assert "MACHINE_CAN_READ != MACHINE_CAN_DEFINE" in invariants
    assert "HUMAN_AGENCY > MACHINE_AUTHORITY" in invariants


def test_library_catalog_entries_are_unique_and_resolve() -> None:
    repository_root, catalog = _load_catalog()
    artifacts = catalog["artifacts"]

    ids = [artifact["id"] for artifact in artifacts]
    paths = [artifact["path"] for artifact in artifacts]

    assert len(ids) == len(set(ids))
    assert len(paths) == len(set(paths))

    missing = [path for path in paths if not (repository_root / path).is_file()]
    assert missing == []


def test_library_catalog_canonical_scope_matches_release_scope() -> None:
    _, catalog = _load_catalog()

    catalog_canonical = {
        artifact["path"]
        for artifact in catalog["artifacts"]
        if artifact["provenance_scope"] == "canonical_public_artifact"
    }

    assert catalog_canonical == set(CANONICAL_PUBLIC_ARTIFACTS)


def test_library_catalog_preserves_interpretation_boundary() -> None:
    _, catalog = _load_catalog()
    policy = catalog["interpretation_policy"]

    assert policy["catalog_is_identity"] is False
    assert policy["classification_is_truth"] is False
    assert policy["uncertainty_is_allowed"] is True
    assert policy["human_self_definition_has_priority"] is True


def test_library_catalog_matches_public_json_schema() -> None:
    _, catalog = _load_catalog()
    schema = json.loads(CATALOG_SCHEMA.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(catalog)
