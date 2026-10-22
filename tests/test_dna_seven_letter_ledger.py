"""Canon and documentation checks for the sourced Seven-Letter Ledger companion."""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SLUG = "DNA_BIBLE_SEVEN_LETTER_LEDGER_ENTER_THE_NET"
CHAPTER = ROOT / "docs" / f"{SLUG}.md"

WITNESSES = (
    "Isaiah 25:7",
    "Isaiah 59:5",
    "Job 8:14",
    "Ezekiel 12:13",
    "Jeremiah 16:16",
    "Proverbs 5:21",
    "Romans 12:2",
    "Isaiah 10:1",
    "Proverbs 23:3",
    "Psalm 124:7",
)

SOURCES = (
    "https://www.mpia.de/news/science/2010-04-lucifer",
    "https://research.ibm.com/topics/cryptography",
    "https://csrc.nist.gov/nist-cyber-history/cryptography/chapter",
    "https://www.ftc.gov/reports/bringing-dark-patterns-light",
    "https://www.ftc.gov/reports/look-behind-screens-examining-data-practices-social-media-video-streaming-services",
    "https://www.ftc.gov/news-events/news/press-releases/2024/01/ftc-order-prohibits-data-broker-x-mode-social-outlogic-selling-sensitive-location-data",
    "https://www.ftc.gov/news-events/news/press-releases/2025/01/ftc-surveillance-pricing-study-indicates-wide-range-personal-data-used-set-individualized-consumer",
    "https://commission.europa.eu/news-and-media/news/digital-services-act-keeping-us-safe-online-2025-09-22_en",
    "https://digital-strategy.ec.europa.eu/en/policies/dsa-vlops",
    "https://www.nist.gov/itl/ai-risk-management-framework",
    "https://digitallibrary.un.org/record/4088727",
    "https://www.yanisvaroufakis.eu/2024/01/13/qa-on-technofeudalism-interviewed-by-lorenzo-tecleme-for-valori-it/",
)


def test_chapter_title_and_story_boundary() -> None:
    content = CHAPTER.read_text(encoding="utf-8")
    assert content.startswith("# 𓂀 THE SEVEN-LETTER LEDGER\n")
    for excerpt in (
        "L.U.C.I.F.E.R.™",
        "HISTORY ≠ ALLEGORY ≠ EVIDENCE OF MISCONDUCT",
        "TEN BIBLICAL WITNESSES AND THE ARCHITECTURE OF DIGITAL AUTHORITY",
        "ENTER THE NET",
        "invented",
        "not a federally registered trademark",
        "do not prove the fiction happened",
        "Techno-federalism",
        "contested political-economic interpretation",
    ):
        assert excerpt.lower() in content.lower(), excerpt
    assert len(re.findall(r"^#\s", content, re.MULTILINE)) == 1  # only the first line is H1


def test_ten_verses_are_distinct_and_the_ezekiel_reference_is_corrected() -> None:
    content = CHAPTER.read_text(encoding="utf-8")
    source_section = content.split("### A. Ten biblical witnesses", 1)[1]
    rows = [line for line in source_section.splitlines() if re.match(r"^\|\s*\d+\s*\|", line)]
    assert len(rows) == 10
    for verse, row in zip(WITNESSES, rows):
        assert verse in row, (verse, row)
    assert "Ezekiel **12:13**, not 26:16" in content
    assert "not a universal prohibition on all profiling" in content


def test_real_world_source_links_are_present_with_explanatory_scope() -> None:
    content = CHAPTER.read_text(encoding="utf-8")
    for url in SOURCES:
        assert url in content, url
    assert "predate this fictional acronym" in content
    assert "not evidence of affiliation or misconduct" in content.lower().replace("**", "")
    assert "They do **not** establish" in content
    assert "NOT DEMONSTRATED" in content


def test_research_chapter_is_linked_in_all_reading_paths() -> None:
    paths = (
        "mkdocs.yml",
        "docs/index.md",
        "docs/2084/index.md",
        "docs/story-universe/index.md",
        "docs/DNA_BIBLE_REVELATION_13_18_LUCIFER.md",
        "docs/DNA_BIBLE_WEB_OVER_ALL_NATIONS.md",
    )
    for name in paths:
        assert SLUG in (ROOT / name).read_text(encoding="utf-8"), name


def test_page_uses_accessible_text_and_no_broken_local_markdown_links() -> None:
    content = CHAPTER.read_text(encoding="utf-8")
    assert content.count("<div") == content.count("</div>")
    assert len(re.findall(r"^~~~", content, re.MULTILINE)) % 2 == 0
    for dest in re.findall(r"\]\(([^)]+)\)", content):
        if dest.startswith(("https://", "http://", "#")):
            continue
        link = (CHAPTER.parent / dest.split("#", 1)[0]).resolve()
        assert link.is_file(), f"Broken local link: {dest}"
