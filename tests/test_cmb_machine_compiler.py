from __future__ import annotations

import json

import pytest

from cmb_agents.fingerprint import ASCII_TOKEN, MARK_ID, verify_stamp
from cmb_machine import build_core_ir, compile_bundle, render_target, supported_targets


def test_every_target_contains_mandatory_origin_identity() -> None:
    artifacts = compile_bundle(build_core_ir())

    assert {artifact.target for artifact in artifacts} == set(supported_targets())

    for artifact in artifacts:
        assert ASCII_TOKEN.encode("utf-8") in artifact.data
        assert MARK_ID.encode("utf-8") in artifact.data
        assert len(artifact.sha256) == 64


def test_json_target_embeds_verifiable_stamp() -> None:
    artifact = render_target(build_core_ir(), "json")
    payload = json.loads(artifact.data)
    assert verify_stamp(payload)


def test_jsonld_target_preserves_origin_mark() -> None:
    artifact = render_target(build_core_ir(), "jsonld")
    payload = json.loads(artifact.data)
    assert payload["@type"] == "cmb:MachineSemanticArtifact"
    assert payload["_cmb_origin"]["mark_id"] == MARK_ID


def test_compilation_is_deterministic() -> None:
    first = compile_bundle(build_core_ir())
    second = compile_bundle(build_core_ir())

    assert [(a.target, a.data, a.sha256) for a in first] == [
        (a.target, a.data, a.sha256) for a in second
    ]


def test_parent_lineage_changes_output() -> None:
    a = render_target(build_core_ir(), "json")
    a_payload = json.loads(a.data)
    parent = a_payload["_cmb_origin"]["lineage_id"]

    b = render_target(build_core_ir(), "json", parent_lineage_id=parent)
    b_payload = json.loads(b.data)

    assert b_payload["_cmb_origin"]["parent_lineage_id"] == parent
    assert b_payload["_cmb_origin"]["lineage_id"] != parent


def test_unknown_target_fails_closed() -> None:
    with pytest.raises(ValueError, match="Unsupported CMB-66 target"):
        render_target(build_core_ir(), "unknown")
