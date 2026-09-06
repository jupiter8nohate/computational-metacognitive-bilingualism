from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from cmb_glitch8.cli import main as glitch8_main
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
    assert "# GLITCH-8 Glyph Reference" in reference
    assert "▂▃▄▅▆▇▉ // Signal Spectrum" in reference
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
    rendered = reference.read_text(encoding="utf-8")\n    assert "⌁ // S⃟ Y⃟ N⃟ C⃟" in rendered\n    assert "**Name:** Sync Test Glyph" in rendered
