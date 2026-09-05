from __future__ import annotations

import json
from pathlib import Path

import pytest

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
