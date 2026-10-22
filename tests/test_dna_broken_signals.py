"""Literary glyphedition checks: ten signals, ten patterns and traceable canon links."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs/dna-codex/BROKEN_SIGNALS.md"
REGISTRY = ROOT / "src/cmb_glitch8/glyphs.v1.json"


def test_all_ten_signals_and_all_ten_pattern_families_are_present() -> None:
    text = PAGE.read_text(encoding="utf-8")
    signal_ids = re.findall(r"<h3>(BRS-\d{3})\b", text)
    pattern_ids = re.findall(r"^### (BRS-P-\d{2})\b", text, flags=re.MULTILINE)
    assert signal_ids == [f"BRS-{i:03d}" for i in range(1, 11)]
    assert pattern_ids == [f"BRS-P-{i:02d}" for i in range(1, 11)]
    assert "not" in text.lower() and "historical" in text.lower()
    assert "not" in text.lower() and "registry" in text.lower()


def test_all_relative_chapter_links_resolve_to_repository_sources() -> None:
    text = PAGE.read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)\s]+)\)", text)
    assert len(links) >= 15
    for link in links:
        if urlsplit(link).scheme:
            assert urlsplit(link).scheme == "https"
            continue
        path = (PAGE.parent / link).resolve()
        assert path.is_relative_to(ROOT)
        assert path.is_file(), f"Missing documented literary backtrace: {link}"


def test_registered_glyph_semantics_are_not_replaced() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    known = {glyph["id"]: glyph for glyph in registry["glyphs"]}
    for key, token in {
        "dual-witness": "𓁇𓁋",
        "portal-threshold": "⚯ ͛ ❾¾",
        "boundary-node": "▕⃝⃤",
        "shock-spark": "⚡︎",
        "falcon-signal": "𓅓",
    }.items():
        assert known[key]["glyph"] == token
    text = PAGE.read_text(encoding="utf-8")
    assert "BOOK-LOCAL" in text.upper() and "registry mutation" in text.lower()


def test_reader_navigation_and_glyph_visuals() -> None:
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    codex = (ROOT / "docs/dna-codex/index.md").read_text(encoding="utf-8")
    stylesheet = (ROOT / "docs/stylesheets/dna-codex.css").read_text(encoding="utf-8")
    assert "dna-codex/BROKEN_SIGNALS.md" in mkdocs
    assert 'href="BROKEN_SIGNALS/"' in codex
    assert ".dna-signal-grid" in stylesheet
    assert "prefers-reduced-motion" in stylesheet
    assert "aria-label" in PAGE.read_text(encoding="utf-8")
