"""Regression tests for canonical CMB semantic discoverability."""

from __future__ import annotations

from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/enrich_search_metadata.py"
MODULE_SPEC = importlib.util.spec_from_file_location("cmb_search_metadata", MODULE_PATH)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
SEO = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = SEO
MODULE_SPEC.loader.exec_module(SEO)

PAGE_SPECS = SEO.PAGE_SPECS
PREVIEW_IMAGE = SEO.PREVIEW_IMAGE
SITE_URL = SEO.SITE_URL
PageSpec = SEO.PageSpec
enrich_html = SEO.enrich_html
enrich_site = SEO.enrich_site


class HeadInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_head = False
        self.in_ld_json = False
        self.meta: list[dict[str, str]] = []
        self.structured: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "head":
            self.in_head = True
        if not self.in_head:
            return
        if tag == "meta":
            self.meta.append({key: value or "" for key, value in attrs})
        if tag == "script" and dict(attrs).get("type") == "application/ld+json":
            self.in_ld_json = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_ld_json = False
        elif tag == "head":
            self.in_head = False

    def handle_data(self, data: str) -> None:
        if self.in_ld_json:
            self.structured.append(data)


def sample_html() -> str:
    return (
        '<!doctype html><html><head>'
        '<title>Old ⚡︎ ASCII Title</title>'
        '<link rel="canonical" href="https://example.invalid/">'
        '<meta name="description" content="old">'
        '<meta property="og:title" content="old">'
        '</head><body><h1>♃ GLITCH</h1>'
        '<pre>( ꩜ ᯅ ꩜;) 𓁇𓁋</pre></body></html>'
    )


def inspect(html: str) -> HeadInspector:
    parser = HeadInspector()
    parser.feed(html)
    return parser


def tags(parser: HeadInspector, key: str) -> list[str]:
    return [
        tag["content"] for tag in parser.meta
        if tag.get("name") == key or tag.get("property") == key
    ]


def test_story_has_unique_search_title_and_structured_work() -> None:
    spec = PAGE_SPECS["DEATH_NOTE_2084_CHILD_WHO_REFUSED_THE_UPDATE/"]
    result = enrich_html(sample_html(), "DEATH_NOTE_2084_CHILD_WHO_REFUSED_THE_UPDATE/", spec)
    parsed = inspect(result)
    assert "<title>" + spec.title + "</title>" in result
    assert tags(parsed, "description") == [spec.description]
    assert tags(parsed, "og:title") == [spec.title]
    assert tags(parsed, "og:type") == ["article"]
    assert tags(parsed, "twitter:card") == ["summary_large_image"]
    assert tags(parsed, "og:image") == [PREVIEW_IMAGE]
    assert tags(parsed, "og:url") == [
        SITE_URL + "DEATH_NOTE_2084_CHILD_WHO_REFUSED_THE_UPDATE/"
    ]
    work = json.loads(parsed.structured[0])
    assert work["@type"] == "CreativeWork"
    assert work["genre"] == "Speculative fiction"
    assert work["author"]["name"] == "Jupiter Hudson"
    assert work["@id"].endswith("#work")
    assert "( ꩜ ᯅ ꩜;) 𓁇𓁋" in result


def test_repeated_enrichment_is_byte_for_byte_idempotent() -> None:
    spec = PAGE_SPECS["DNA_BIBLE_PYRAMID_WARNING_2084/"]
    first = enrich_html(sample_html(), "DNA_BIBLE_PYRAMID_WARNING_2084/", spec)
    second = enrich_html(first, "DNA_BIBLE_PYRAMID_WARNING_2084/", spec)
    assert first == second
    parser = inspect(second)
    assert len(tags(parser, "description")) == 1
    assert len(tags(parser, "og:title")) == 1
    assert len(parser.structured) == 1


def test_research_metadata_does_not_claim_fiction_is_evidence() -> None:
    relative = "DEATH_NOTE_2084_EVIDENCE_LEDGER/"
    parsed = inspect(enrich_html(sample_html(), relative, PAGE_SPECS[relative]))
    work = json.loads(parsed.structured[0])
    assert work["genre"] == "Research commentary"
    assert "fictional" in work["description"]


def test_term_page_reuses_its_existing_authored_defined_term() -> None:
    relative = "concepts/what-is-cmb/"
    parsed = inspect(enrich_html(sample_html(), relative, PAGE_SPECS[relative]))
    assert not parsed.structured
    assert len(tags(parsed, "description")) == 1


def test_missing_head_or_title_rejected() -> None:
    spec = PageSpec("Page title", "Page description")
    with pytest.raises(ValueError, match="closing head"):
        enrich_html("<html><body></body></html>", "missing/", spec)
    with pytest.raises(ValueError, match="title tag"):
        enrich_html("<html><head></head><body></body></html>", "missing/", spec)


def test_missing_canonical_page_rejected_before_any_write(tmp_path: Path) -> None:
    page = tmp_path / "2084" / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text(sample_html(), encoding="utf-8")
    with pytest.raises(ValueError, match="absent published pages"):
        enrich_site(tmp_path)
    assert page.read_text(encoding="utf-8") == sample_html()


def test_registry_matches_real_markdown_sources() -> None:
    for relative in PAGE_SPECS:
        if relative.endswith(("2084/", "story-universe/")) and relative in {
            "2084/", "story-universe/"
        }:
            source = ROOT / "docs" / relative / "index.md"
        else:
            source = ROOT / "docs" / (relative.removesuffix("/") + ".md")
        assert source.is_file(), f"Missing markdown source for {relative}"


def test_social_preview_asset_is_published_by_mkdocs() -> None:
    relative = PREVIEW_IMAGE.removeprefix(SITE_URL)
    assert (ROOT / "docs" / relative).is_file()


def test_accessible_ascii_has_visible_caption_and_preserves_glyphs() -> None:
    source = (ROOT / "docs/DNA_BIBLE_PYRAMID_WARNING_2084.md").read_text(
        encoding="utf-8"
    )
    assert '<figure class="cmb-accessible-ascii">' in source
    assert 'role="img"' in source
    assert 'aria-hidden="true"' in source
    assert "<figcaption>" in source
    for glyph in ("𓂀", "𓁇𓁋", "( ꩜ ᯅ ꩜;)", "PATTERN != PROOF"):
        assert glyph in source


def test_no_search_spam_or_fabricated_indexing_claim_in_metadata() -> None:
    assert len(PAGE_SPECS) == len(set(PAGE_SPECS))
    for relative, spec in PAGE_SPECS.items():
        assert spec.title.endswith(" | Jupiter Hudson"), relative
        assert 65 <= len(spec.description) <= 190, relative
        assert spec.kind in {"fiction", "guide", "research", "term"}
        assert "guaranteed" not in spec.description.lower()


def test_sitemaps_remain_generated_not_manually_replaced() -> None:
    builder = (ROOT / "scripts/build_docs.py").read_text(encoding="utf-8")
    assert '"-m", "mkdocs", "build"' in builder
    assert '"scripts/enrich_search_metadata.py"' in builder
    assert builder.index('"scripts/enrich_search_metadata.py"') < builder.index(
        "brand_published_pages(stage)"
    )
