"""Regression checks for the Revelation 13:18 D.N.A. Bible companion scroll."""

from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "docs/DNA_BIBLE_REVELATION_13_18_LUCIFER.md"
PAGE_PATH = "DNA_BIBLE_REVELATION_13_18_LUCIFER.md"

GLYPHS = (
    "�", "𒈔", "𒅒", "𒇫", "𒄆", "(𓁹 𓁹)", "⍨⃝", "📷",
    "⚯", "͛", "❾", "¾", "▕⃝⃤", "⚡︎", "𓅓", "(⚆_⚆)",
    "🜏", "⛧⃝", "𓄃", "𝐋𝐮𝐜𝐢𝐟𝐞𝐫", "𓂀", "𖤍",
    "𓌵", "݁", "ᛪ", "༙",
)


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_exact_revelation_1318_title() -> None:
    expected = (
        '# Revelation 13:18: "Here is wisdom. Let him that hath understanding '
        "count the number of the beast: for it is the number of a man; "
        'and his number is Six hundred threescore and six."'
    )
    assert CHAPTER.is_file()
    assert read("docs/" + PAGE_PATH).startswith(expected)


def test_all_original_new_glyphs_have_textual_registry_entries() -> None:
    chapter = read("docs/" + PAGE_PATH)
    registry = chapter.split("## 07 // GLITCHOLOGY SYMBOL REGISTRY:", 1)[1]
    assert "Composite name:" in registry
    assert "GLITCH://FALSE_LIGHT_LEDGER_BACKTRACE" in registry
    for glyph in GLYPHS:
        assert "**" + glyph + "**" in registry, f"Missing symbol: {glyph!r}"


def test_machine_readable_glyph_registry_matches_the_chapter() -> None:
    data = json.loads(read("library/dna-lucifer-2084-glyphs.v1.json"))
    assert data["schema_version"] == "dna.lucifer-glyph-canon.v1"
    assert data["source_document"] == "docs/" + PAGE_PATH
    assert data["trademark_claim"]["designation"] == "L.U.C.I.F.E.R.™"
    assert data["trademark_claim"]["federal_registration_asserted"] is False
    glyphs = {entry["glyph"] for entry in data["symbols"]}
    assert glyphs == set(GLYPHS)
    assert len(data["symbols"]) == len(GLYPHS)
    assert data["claims"]["glyph_historical_meanings_claimed"] is False


def test_canonical_acronym_and_status_are_explicit() -> None:
    chapter = read("docs/" + PAGE_PATH)
    trademark = read("docs/DNA_BIBLE_TRADEMARK.md")
    for letter, expansion in [
        ("L", "Ledger"),
        ("U", "Universal"),
        ("C", "Compliance"),
        ("I", "Inference"),
        ("F", "Forecasting"),
        ("E", "Extraction"),
        ("R", "Ranking"),
    ]:
        assert "| **" + letter + "** | **" + expansion + "** |" in chapter

    for text in (chapter, trademark):
        assert "L.U.C.I.F.E.R.™" in text
        assert "not" in text.lower() and "registration" in text.lower()
    assert "No ® registration claim is made." in chapter


def test_page_is_discoverable_in_reading_paths() -> None:
    for path in (
        "mkdocs.yml",
        "docs/index.md",
        "docs/2084/index.md",
        "docs/story-universe/index.md",
        "docs/DNA_BIBLE_TRADEMARK.md",
    ):
        assert PAGE_PATH.replace(".md", "") in read(path), path


def test_story_distinguishes_scripture_from_fiction_and_enforcement() -> None:
    chapter = read("docs/" + PAGE_PATH)
    assert "not a claim that Revelation predicts the Internet" in chapter
    assert "not a retroactive sixth installment" in chapter
    assert "not a deployed security system" in chapter
    assert "independent review" in chapter.lower()
    assert "PATTERN != PROOF" not in chapter or "OBSERVATION != UNDERSTANDING" in chapter
