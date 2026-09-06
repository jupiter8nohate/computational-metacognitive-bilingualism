from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from cmb_glitch8.cli import main as glitch8_main
from cmb_glitch8.glitch_ir import assert_expected_result, evaluate_vector, load_vector
from cmb_glitch8.registry import GlyphRegistryError, load_registry, parse_statement


def test_bundled_registry_is_valid_and_signal_spectrum_is_loadable() -> None:
    registry = load_registry()
    signal = registry.get("▂▃▄▅▆▇▉")
    assert signal["name"] == "Signal Spectrum"
    assert signal["cmb_invariant"] == "SIGNAL_STRENGTH != PROOF"
    assert signal["runtime_behavior"]["levels"]["▇"] == "VERY_STRONG_SIGNAL"


def test_alias_lookup_uses_canonical_entry() -> None:
    registry = load_registry()
    assert registry.get("ʕ...✧")["id"] == "vulnerability-state"


def test_parse_statement_uses_registry_glyph() -> None:
    statement = parse_statement(
        "⁇ [GO] profile_prediction :: UNVERIFIED :: HUMAN_REVIEW"
    )
    assert statement.glyph_id == "compound-uncertainty"
    assert statement.runtime == "GO"
    assert statement.state == "UNVERIFIED"
    assert statement.authority == "HUMAN_REVIEW"


def test_unknown_runtime_is_rejected() -> None:
    with pytest.raises(GlyphRegistryError, match="Unknown runtime"):
        parse_statement("﹖ [XYZ] claim :: UNKNOWN :: WITHHOLD")


def test_add_bumps_registry_version_and_rejects_semantic_collision(
    tmp_path: Path,
) -> None:
    registry = load_registry()
    path = tmp_path / "glyphs.json"
    path.write_text(
        json.dumps(registry.data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    writable = load_registry(path)

    entry = {
        "id": "test-glyph",
        "glyph": "⌁",
        "aliases": [],
        "name": "Test Glyph",
        "categories": ["observation"],
        "semantic_key": "test_semantics",
        "version": "0.1.0",
        "status": "experimental",
        "definition": "Test-only glyph.",
        "cmb_invariant": "TEST != PRODUCTION",
        "human_semantics": "Used only by tests.",
        "machine_semantics": "TEST_GLYPH",
        "runtime_behavior": {"type": "marker"},
        "example": "⌁ [G8] test :: EXPERIMENTAL :: NO_AUTHORITY",
        "created_at": "2026-09-05",
        "author": "Test",
    }

    old_version = writable.language_version
    writable.add(entry)
    writable.write()

    assert writable.language_version != old_version
    assert load_registry(path).get("⌁")["id"] == "test-glyph"

    collision = dict(entry)
    collision["id"] = "other-test-glyph"
    collision["glyph"] = "⌁⌁"
    with pytest.raises(GlyphRegistryError, match="Semantic collision"):
        writable.add(collision)


def test_reference_is_generated_from_registry() -> None:
    reference = load_registry().render_reference()
    assert "G⃟ L⃟ I⃟ T⃟ C⃟ H⃟" in reference
    assert "**GLITCH-8 Glyph Reference**" in reference
    assert "**Name:** Signal Spectrum" in reference
    assert "Edit the registry, not this file" in reference


def test_individual_signal_level_parses() -> None:
    statement = parse_statement(
        "▇ [GO] correlation :: HIGH_SIGNAL :: UNPROVEN"
    )
    assert statement.glyph_id == "signal-spectrum"
    assert statement.glyph == "▂▃▄▅▆▇▉"


def test_registry_matches_json_schema() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads(
        (root / "schemas" / "glitch8.glyph-registry.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    data = json.loads(
        (root / "src" / "cmb_glitch8" / "glyphs.v1.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema).validate(data)


def test_public_registry_mirror_matches_canonical_bytes() -> None:
    root = Path(__file__).resolve().parents[1]
    canonical = root / "src" / "cmb_glitch8" / "glyphs.v1.json"
    public = root / "library" / "glitch8.glyphs.v1.json"
    assert public.read_bytes() == canonical.read_bytes()


def test_every_registered_example_is_parseable() -> None:
    registry = load_registry()
    for entry in registry.data["glyphs"]:
        statement = parse_statement(entry["example"], registry)
        assert statement.glyph_id == entry["id"]


def test_generated_reference_matches_registry() -> None:
    root = Path(__file__).resolve().parents[1]
    generated = (root / "books" / "GLITCH8_GLYPH_REFERENCE.md").read_text(
        encoding="utf-8"
    )
    assert generated == load_registry().render_reference()


def test_cli_add_auto_syncs_repository_views(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    source_dir = root / "src" / "cmb_glitch8"
    source_dir.mkdir(parents=True)
    canonical = source_dir / "glyphs.v1.json"
    canonical.write_text(
        json.dumps(load_registry().data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    definition = root / "new-glyph.json"
    definition.write_text(
        json.dumps(
            {
                "id": "sync-test-glyph",
                "glyph": "⌁",
                "aliases": [],
                "name": "Sync Test Glyph",
                "categories": ["observation"],
                "semantic_key": "sync_test_semantics",
                "version": "0.1.0",
                "status": "experimental",
                "definition": "Verifies one-command synchronization.",
                "cmb_invariant": "SYNC != AUTHORITY",
                "human_semantics": "Test-only synchronization glyph.",
                "machine_semantics": "SYNC_TEST_GLYPH",
                "runtime_behavior": {"type": "marker"},
                "example": "⌁ [G8] sync :: EXPERIMENTAL :: NO_AUTHORITY",
                "created_at": "2026-09-05",
                "author": "Test",
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(root)
    assert glitch8_main(["glyph", "add", str(definition)]) == 0

    public = root / "library" / "glitch8.glyphs.v1.json"
    reference = root / "books" / "GLITCH8_GLYPH_REFERENCE.md"
    assert public.read_bytes() == canonical.read_bytes()
    rendered = reference.read_text(encoding="utf-8")
    assert "⌁ // S⃟ Y⃟ N⃟ C⃟" in rendered
    assert "**Name:** Sync Test Glyph" in rendered

def test_official_composite_protocol_sequence() -> None:
    registry = load_registry()
    expected = {
        f"GLT-{value:04d}": token
        for value, token in zip(
            range(37, 47),
            [
                "GLITCH://MIRROR_CONTEST",
                "GLITCH://PATTERN_TRIAL",
                "GLITCH://NULL_BREATH",
                "GLITCH://CONSENT_THRESHOLD",
                "GLITCH://ARCHIVE_GHOST",
                "GLITCH://CASCADING_ERROR",
                "GLITCH://ENCODING_RUIN",
                "GLITCH://HUMAN_APPEAL",
                "GLITCH://QUESTION_GATE",
                "GLITCH://RECOVERY_WITNESS",
            ],
            strict=True,
        )
    }

    for alias, token in expected.items():
        entry = registry.get(alias)
        assert entry["glyph"] == token
        assert entry["status"] == "canonical"
        assert entry["runtime_behavior"]["type"] == "composite_protocol"
        assert parse_statement(entry["example"], registry).glyph_id == entry["id"]


def test_figlet_3d_diagonal_artifact_is_byte_stable() -> None:
    root = Path(__file__).resolve().parents[1]
    artifact = (
        root
        / "examples"
        / "polyglot"
        / "glitchology_registry_3d_runtime"
        / "FIGLET_3D_DIAGONAL.txt"
    )
    expected = (
        "   ______        ______        ______\n"
        "  /_____/\\      /_____/\\      /_____/\n"
        "  \\::::_\\/_     \\::::_\\/_     \\::::_\\\n"
        "   \\:\\/___/\\     \\:\\/___/\\     \\:\\/___/\\\n"
        "    \\_::._\\:\\     \\::___\\/_     \\::___\\/_\n"
        "      /____\\:\\     \\:\\____/\\     \\:\\____/\\\n"
        "      \\_____\\/      \\_____\\/      \\_____\\/\n"
    )
    assert artifact.read_text(encoding="utf-8") == expected



def test_glt_8101_is_registered_as_canonical_synchrony() -> None:
    registry = load_registry()
    entry = registry.get("GLT-8101")
    assert entry["glyph"] == "GLITCH://CANONICAL_SYNCHRONY"
    assert entry["status"] == "canonical"
    assert entry["runtime_behavior"]["contract"] == "GLITCH-IR-1"
    assert entry["runtime_behavior"]["type"] == "composite_protocol"


def test_cpp_runtime_tag_is_explicit() -> None:
    statement = parse_statement(
        "GLITCH://CANONICAL_SYNCHRONY [CPP] GLT-8101-V001 :: "
        "CONFORMANCE_STABLE :: HUMAN_AUTHORITY_PRESERVED"
    )
    assert statement.runtime == "CPP"
    assert statement.glyph_id == "canonical-synchrony-protocol"


def test_glitch_ir_vector_matches_schema_and_reference_evaluator() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads(
        (root / "schemas" / "glitch-ir.v1.schema.json").read_text(encoding="utf-8")
    )
    vector_path = (
        root / "conformance" / "glitch-ir" / "v1" / "GLT-8101-V001.json"
    )
    vector = load_vector(vector_path)
    Draft202012Validator(schema).validate(vector)

    result = evaluate_vector(vector)
    assert_expected_result(vector, result)
    assert result.canonical_line() == (
        "GLT-8101-V001|1.0.0|BACKTRACE|GLT-0036|CONTESTED\n"
    )


def test_glitch_ir_projection_matches_normative_json() -> None:
    root = Path(__file__).resolve().parents[1]
    base = root / "conformance" / "glitch-ir" / "v1"
    vector = json.loads((base / "GLT-8101-V001.json").read_text(encoding="utf-8"))
    expected = "\n".join(
        [
            f"vector_id={vector['vector_id']}",
            f"protocol_version={vector['protocol_version']}",
            f"verification_label={vector['claim']['verification_label']}",
            f"evidence={vector['claim']['evidence']}",
            f"source={vector['claim']['source']}",
            f"human_review={vector['human_review']}",
            f"expected_verdict={vector['expected_result']['verdict']}",
            f"expected_operator={vector['expected_result']['operator']}",
            f"expected_state={vector['expected_result']['state']}",
        ]
    ) + "\n"
    assert (base / "GLT-8101-V001.txt").read_text(encoding="utf-8") == expected
