from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from cmb_glitch8.cli import main as glitch8_main
from cmb_glitch8.glitch3d import Glitch3DError, parse_glitch3d, render_spatial_summary


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = (
    ROOT
    / "examples"
    / "polyglot"
    / "glitchology_registry_3d_runtime"
    / "GLITCH_3D_SOURCE_FRACTURE.g3d"
)


def test_glitch3d_example_validates_against_schema() -> None:
    source = EXAMPLE.read_text(encoding="utf-8")
    program = parse_glitch3d(source)
    schema = json.loads(
        (ROOT / "schemas" / "glitch-3d.v1.schema.json").read_text(encoding="utf-8")
    )

    Draft202012Validator(schema).validate(program.to_dict())
    assert program.program_id == "source-fracture-3d"
    assert len(program.nodes) == 5
    assert len(program.edges) == 4
    assert program.nodes[-1].kind == "HUMAN"
    assert program.nodes[-1].z == 4


def test_glitch3d_digest_is_deterministic() -> None:
    source = EXAMPLE.read_text(encoding="utf-8")
    first = parse_glitch3d(source)
    second = parse_glitch3d(source)

    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.sha256() == second.sha256()
    assert len(first.sha256()) == 64


def test_glitch3d_render_exposes_semantic_layers() -> None:
    program = parse_glitch3d(EXAMPLE.read_text(encoding="utf-8"))
    rendered = render_spatial_summary(program)

    assert "GLITCH://3D_RUNTIME" in rendered
    assert "Z=0 EVENT" in rendered
    assert "Z=4 HUMAN" in rendered
    assert "semantic --BACKTRACE--> source" in rendered
    assert "semantic --ESCALATE--> human" in rendered
    assert "SHA256://" in rendered


def test_glitch3d_rejects_kind_depth_mismatch() -> None:
    source = """GLITCH-3D/1
PROGRAM broken
NODE event X=0 Y=0 Z=0 KIND=MACHINE STATE=RECEIVED
INVARIANT PATTERN != PROOF
"""
    with pytest.raises(Glitch3DError, match="requires KIND=EVENT"):
        parse_glitch3d(source)


def test_glitch3d_backtrace_must_target_provenance() -> None:
    source = """GLITCH-3D/1
PROGRAM broken
NODE semantic X=0 Y=0 Z=2 KIND=SEMANTIC STATE=CONTESTED
NODE machine X=0 Y=1 Z=1 KIND=MACHINE STATE=UNKNOWN
EDGE semantic machine OP=BACKTRACE
INVARIANT SIGNAL != SOURCE
"""
    with pytest.raises(Glitch3DError, match="BACKTRACE must target a PROVENANCE node"):
        parse_glitch3d(source)


def test_glitch3d_human_entry_requires_sovereignty_boundary() -> None:
    source = """GLITCH-3D/1
PROGRAM broken
NODE semantic X=0 Y=0 Z=2 KIND=SEMANTIC STATE=CONTESTED
NODE human X=1 Y=1 Z=4 KIND=HUMAN STATE=REVIEW_REQUIRED
EDGE semantic human OP=ESCALATE
INVARIANT HUMAN_AGENCY > MACHINE_AUTHORITY
"""
    with pytest.raises(Glitch3DError, match="HUMAN_AUTHORITY_REQUIRED boundary"):
        parse_glitch3d(source)


def test_glitch3d_cli_validate_and_parse(capsys: pytest.CaptureFixture[str]) -> None:
    assert glitch8_main(["3d", "validate", str(EXAMPLE)]) == 0
    validated = capsys.readouterr().out
    assert "VALID GLITCH-3D/1.0.0" in validated
    assert "sha256=" in validated

    assert glitch8_main(["3d", "parse", str(EXAMPLE)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "glitch3d.program.v1"
    assert payload["axes"]["z"] == "SEMANTIC_DEPTH"
