from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from cmb_provenance.canon import get_node, load_canon, related_nodes

ROOT = Path(__file__).resolve().parents[1]
CANON_PATH = ROOT / "library" / "canon.json"
SCHEMA_PATH = ROOT / "schemas" / "cmb.canon.v1.schema.json"
CATALOG_PATH = ROOT / "library" / "catalog.json"


def test_canon_matches_public_schema() -> None:
    canon = json.loads(CANON_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(canon)


def test_canon_graph_has_no_dangling_edges() -> None:
    canon = load_canon(CANON_PATH)
    ids = {node["id"] for node in canon["nodes"]}

    assert len(ids) == len(canon["nodes"])
    assert all(edge["from"] in ids and edge["to"] in ids for edge in canon["edges"])


def test_canon_artifact_ids_resolve_to_catalog() -> None:
    canon = load_canon(CANON_PATH)
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    known_artifacts = {artifact["id"] for artifact in catalog["artifacts"]}

    referenced = {
        artifact_id
        for node in canon["nodes"]
        for artifact_id in node["artifact_ids"]
    }
    assert referenced <= known_artifacts


def test_canon_repository_paths_resolve_for_linked_nodes() -> None:
    canon = load_canon(CANON_PATH)

    missing: list[str] = []
    for node in canon["nodes"]:
        if node["status"] == "unlinked":
            assert node["artifact_ids"] == []
            assert node["repository_paths"] == []
            continue

        assert node["artifact_ids"] or node["repository_paths"]
        for relative_path in node["repository_paths"]:
            if not (ROOT / relative_path).exists():
                missing.append(relative_path)

    assert missing == []


def test_canon_preserves_evidence_boundaries() -> None:
    canon = load_canon(CANON_PATH)
    policy = canon["interpretation_policy"]

    assert policy["declaration_is_proof"] is False
    assert policy["hash_is_authorship"] is False
    assert policy["signature_is_copyright"] is False
    assert policy["timestamp_is_truth"] is False
    assert policy["provenance_is_legal_judgment"] is False
    assert policy["human_self_definition_has_priority"] is True
    assert policy["unlinked_node_claims_artifact_presence"] is False


def test_canon_navigation_is_deterministic() -> None:
    canon = load_canon(CANON_PATH)
    node = get_node(canon, "cmb-core")
    relations = related_nodes(canon, "cmb-core")

    assert node["label"] == "CMB Core"
    assert {item["node"] for item in relations} >= {
        "provenance-engine",
        "digital-library",
        "fgc-symbolic-layer",
        "cmb-z13",
        "dna",
        "cmb-edu",
        "the-convergence",
    }
