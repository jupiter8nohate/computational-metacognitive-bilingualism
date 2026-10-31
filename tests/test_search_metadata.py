"""Regression tests for canonical CMB semantic discoverability."""

from __future__ import annotations

from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import gzip
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

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
        "<!doctype html><html><head>"
        "<title>Old ⚡︎ ASCII Title</title>"
        '<link rel="canonical" href="https://example.invalid/">'
        '<meta name="description" content="old">'
        '<meta property="og:title" content="old">'
        "</head><body><h1>♃ GLITCH</h1>"
        "<pre>( ꩜ ᯅ ꩜;) 𓁇𓁋</pre></body></html>"
    )


def inspect(html: str) -> HeadInspector:
    parser = HeadInspector()
    parser.feed(html)
    return parser


def tags(parser: HeadInspector, key: str) -> list[str]:
    return [
        tag["content"]
        for tag in parser.meta
        if tag.get("name") == key or tag.get("property") == key
    ]


def test_story_has_unique_search_title_and_structured_work() -> None:
    spec = PAGE_SPECS["DEATH_NOTE_2084_CHILD_WHO_REFUSED_THE_UPDATE/"]
    result = enrich_html(
        sample_html(), "DEATH_NOTE_2084_CHILD_WHO_REFUSED_THE_UPDATE/", spec
    )
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
            "2084/",
            "story-universe/",
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


def test_mkdocs_hook_honors_authored_biography_front_matter() -> None:
    page = SimpleNamespace(
        url="JUPITER_HUDSON_BIOGRAPHY/",
        title="Navigation title",
        meta={
            "title": "Jupiter Hudson: Biography and Selected Work",
            "description": "An authored biography with attribution and evidence boundaries.",
        },
        content="<p>Unrelated fallback paragraph that should not replace authored metadata.</p>",
    )
    result = SEO.on_post_page(sample_html(), page=page, config={"site_url": SITE_URL})
    assert "<title>" + page.meta["title"] + "</title>" in result
    assert tags(inspect(result), "description") == [page.meta["description"]]
    assert result.split("</head>")[1] == sample_html().split("</head>")[1]
    assert not inspect(
        result
    ).structured  # Retain the authored ProfilePage; do not invent fiction.


def test_all_page_hook_uses_visible_prose_without_inventing_fiction() -> None:
    prose = "Cognitive sovereignty describes human control over meaning, judgment and self-definition when interacting with computational systems."
    page = SimpleNamespace(
        url="concepts/cognitive-sovereignty/",
        title="Concepts / Cognitive Sovereignty",
        meta={},
        content=(
            '<script type="application/ld+json">{"description":"Not visible prose"}</script>'
            "<nav><p>Navigation should not supply an article description or title.</p></nav>"
            '<p aria-hidden="true"><span>Hidden glyph commentary must not become a search description.</span></p>'
            "<pre><p>Code must not become a description even when it contains many words.</p></pre>"
            f"<h1>Cognitive Sovereignty</h1><p>{prose}</p>"
        ),
    )
    result = SEO.on_post_page(sample_html(), page=page, config={"site_url": SITE_URL})
    assert "<title>Cognitive Sovereignty | CMB</title>" in result
    assert tags(inspect(result), "description") == [prose]
    assert not inspect(result).structured


def test_head_repair_replaces_conflicting_canonicals_and_titles_once() -> None:
    original = sample_html().replace(
        "</head>",
        '<link rel="alternate canonical" href="https://wrong.invalid/"><title>Duplicate</title></head>',
    )
    result = enrich_html(
        original, "concepts/what-is-cmb/", PAGE_SPECS["concepts/what-is-cmb/"]
    )
    assert result.count('rel="canonical"') == 1
    assert "https://wrong.invalid/" not in result
    assert "https://example.invalid/" not in result
    assert result.count("<title>") == 1
    assert (
        enrich_html(
            result, "concepts/what-is-cmb/", PAGE_SPECS["concepts/what-is-cmb/"]
        )
        == result
    )


def test_summary_shortens_at_a_word_boundary_and_requires_prose() -> None:
    summary = SEO.summarize_content(
        "<p>" + "Human agency retains authority over personal meaning. " * 8 + "</p>"
    )
    assert len(summary) <= 190
    assert summary.endswith("…")
    with pytest.raises(ValueError, match="authored description"):
        SEO.summarize_content("<h1>Only glyphs</h1><pre>CODE</pre>")


def test_source_dates_ignore_checkout_mtime_and_omit_dirty_sources(
    tmp_path: Path,
) -> None:
    source = tmp_path / "docs/example.md"
    source.parent.mkdir()
    source.write_text("# Example\n\nAuthored content.\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "docs/example.md"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "Original content",
        ],
        env={
            **os.environ,
            "GIT_AUTHOR_DATE": "2026-10-10T12:00:00Z",
            "GIT_COMMITTER_DATE": "2026-10-10T12:00:00Z",
        },
        check=True,
    )
    os.utime(source, None)
    date = SEO.source_revision_dates(tmp_path)["docs/example.md"]
    assert date.replace("+00:00", "Z") == "2026-10-10T12:00:00Z"
    source.write_text("# Example\n\nUncommitted changes.\n", encoding="utf-8")
    assert "docs/example.md" not in SEO.source_revision_dates(tmp_path)


def test_sitemap_finalization_adds_static_routes_and_synchronizes_gzip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sitemap = tmp_path / "sitemap.xml"
    sitemap.write_text(
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<url><loc>{SITE_URL}</loc><lastmod>2099-01-01</lastmod></url></urlset>",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        SEO,
        "source_revision_dates",
        lambda root: {"docs/index.md": "2026-10-10T12:00:00Z"},
    )
    assert SEO.finalize_sitemap(tmp_path) == 3
    ns = {"s": SEO.SITEMAP_NS[1:-1]}
    root = ET.parse(sitemap).getroot()
    entries = {node.findtext("s:loc", namespaces=ns): node for node in root}
    assert (
        entries[SITE_URL].findtext("s:lastmod", namespaces=ns) == "2026-10-10T12:00:00Z"
    )
    assert SITE_URL + "spiders-internet/" in entries
    assert SITE_URL + "playground/" in entries
    assert entries[SITE_URL + "spiders-internet/"].find("s:lastmod", ns) is None
    assert (
        gzip.decompress((tmp_path / "sitemap.xml.gz").read_bytes())
        == sitemap.read_bytes()
    )
    before = sitemap.read_bytes()
    SEO.finalize_sitemap(tmp_path)
    assert sitemap.read_bytes() == before
