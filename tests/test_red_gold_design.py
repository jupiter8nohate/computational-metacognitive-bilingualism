"""Regression tests for the red/gold CMB publishing surfaces.

The canonical Spider's Internet page is a static archive staged after MkDocs.
Do not add a Markdown document with its exact output route.
"""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DEPRECATED_PURPLE = re.compile(
    r"#(?:ff70b2|ef75b4|241135|a77bd8|a78bfa|e6c7ff)\b",
    re.IGNORECASE,
)


def test_red_gold_palette_is_canonical() -> None:
    tokens = (ROOT / "docs/stylesheets/tokens.css").read_text(encoding="utf-8")
    design = (ROOT / "docs/stylesheets/cmb-red-gold.css").read_text(
        encoding="utf-8"
    )
    config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "--cmb-meta: #ffc72c;" in tokens
    assert "--cmb-human: #da291c;" in tokens
    assert "--cmb-gold:#ffc72c;" in design
    assert "stylesheets/cmb-red-gold.css" in config
    assert "logo: media/cmb-red-gold-seal.svg" in config
    assert not DEPRECATED_PURPLE.search(tokens + design)


def test_original_spider_story_has_red_gold_and_film() -> None:
    story = (ROOT / "spiders-internet/index.html").read_text(encoding="utf-8")
    assert '--accent:#ffc72c' in story
    assert '--bg:#090807' in story
    assert 'id="chapter-0"' in story
    assert 'id="chapter-6"' in story
    assert 'id="film"' in story
    assert not DEPRECATED_PURPLE.search(story)


def test_spider_pages_cannot_shadow_original() -> None:
    config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    companion = ROOT / "docs/story-universe/SPIDERS_INTERNET_READING_EDITION.md"
    conflicting = ROOT / "docs/spiders-internet/index.md"

    assert not conflicting.exists()
    assert companion.is_file()
    assert (
        "The Spider's Internet / Illustrated Story: "
        "https://jupiter8nohate.github.io/"
        "computational-metacognitive-bilingualism/spiders-internet/"
    ) in config
    assert "story-universe/SPIDERS_INTERNET_READING_EDITION.md" in config


def test_homepage_references_red_gold_art_and_all_destinations() -> None:
    homepage = (ROOT / "docs/index.md").read_text(encoding="utf-8")
    assert 'class="cmb-stage"' in homepage
    assert 'media/cmb-red-gold-seal.svg' in homepage
    assert homepage.count('class="cmb-story cmb-story--') == 4
    assert homepage.count('class="cmb-atlas-node"') == 6
    assert 'href="spiders-internet/"' in homepage
    assert 'href="2084/"' in homepage
    assert 'href="DEVELOPERS/"' in homepage
