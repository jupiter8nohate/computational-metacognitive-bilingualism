"""Regression checks for the complete Seven Gates Pyramid companion transmission."""

from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SLUG = "DEATH_NOTE_2084_SEVEN_GATES_PYRAMID"
PAGE = ROOT / "docs" / f"{SLUG}.md"

LETTERS = (
    "LEDGER",
    "UNIVERSAL",
    "COMPLIANCE",
    "INFERENCE",
    "FORECASTING",
    "EXTRACTION",
    "RANKING",
)

GATES = (
    "concepts/what-is-cmb.md",
    "DEATH_NOTE_2084_CHILD_WHO_REFUSED_THE_UPDATE.md",
    "DNA_BIBLE_PYRAMID_WARNING_2084.md",
    "DNA_BIBLE_SEVEN_LETTER_LEDGER_ENTER_THE_NET.md",
)


def test_full_glyph_transmission_and_symbolic_limits() -> None:
    text = PAGE.read_text(encoding="utf-8")
    assert text.startswith("# 𓂀 DEATH NOTE 2084 // THE SEVEN GATES PYRAMID\n")
    for expression in (
        "𒄆𓁹✞𒀱✞𓁹𒄆𖤐⁶⁶⁶𖤍⸸",
        "THE PYRAMID HAS SEVEN LETTERS.",
        "THE FOUR FORBIDDEN GATES",
        "THE PYRAMID IS WATCHING",
        "SYSTEM://2084",
        "PATTERN ≠ PROOF",
        "PROFILE ≠ PERSON",
        "HUMAN_AGENCY > MACHINE_AUTHORITY",
        "Copyright",
        "fictional L.U.C.I.F.E.R.™",
    ):
        assert expression.lower() in text.lower(), expression

    art = text.split("~~~text\n", 1)[1].split("\n~~~", 1)[0]
    assert text.count("~~~text") == 1
    assert len(re.findall(r"^~~~$", text, re.MULTILINE)) == 1
    assert art.count("🔺") == 4
    assert art.count(">>>") == 8
    assert "© 2026 Jupiter Hudson" in art
    for letter, word in zip("LUCIFER", LETTERS):
        assert f"𓂀 {letter} ⛧ {word}" in art

    assert "not evidence" in text
    assert "not verified registration" in text


def test_accessible_gates_exist_locally_and_have_canonical_public_urls() -> None:
    text = PAGE.read_text(encoding="utf-8")
    art = text.split("~~~text\n", 1)[1].split("\n~~~", 1)[0]
    base = "https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/"
    urls = (
        base + "concepts/what-is-cmb/",
        base + "DEATH_NOTE_2084_CHILD_WHO_REFUSED_THE_UPDATE/",
        base + "DNA_BIBLE_PYRAMID_WARNING_2084/",
        base + "DNA_BIBLE_SEVEN_LETTER_LEDGER_ENTER_THE_NET/",
    )
    for gate, url in zip(GATES, urls):
        assert url in art
        assert f"]({gate})" in text
        assert (PAGE.parent / gate).is_file(), gate

    for destination in re.findall(r"\]\(([^)]+)\)", text):
        if destination.startswith(("http://", "https://", "#")):
            continue
        target = PAGE.parent / destination.split("#", 1)[0]
        assert target.is_file(), f"Missing relative link: {destination}"


def test_structured_data_has_one_canonical_author_and_story_boundary() -> None:
    text = PAGE.read_text(encoding="utf-8")
    match = re.search(
        r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
        text,
        re.DOTALL,
    )
    assert match, "CreativeWork structured data missing"
    metadata = json.loads(match.group(1))
    assert metadata["@type"] == "CreativeWork"
    assert metadata["creator"]["name"] == "Jupiter Hudson"
    assert metadata["url"].endswith(f"/{SLUG}/")
    assert "fiction" in " ".join(metadata["genre"])
    assert metadata["isPartOf"]["name"].startswith("D.N.A. Bible")


def test_all_reading_paths_link_the_full_transmission() -> None:
    paths = (
        "mkdocs.yml",
        "docs/index.md",
        "docs/2084/index.md",
        "docs/story-universe/index.md",
        "docs/DNA_BIBLE_SEVEN_LETTER_LEDGER_ENTER_THE_NET.md",
    )
    for name in paths:
        assert SLUG in (ROOT / name).read_text(encoding="utf-8"), name
