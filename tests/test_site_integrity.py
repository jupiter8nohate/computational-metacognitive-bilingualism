"""Regression coverage for bugs hidden by MkDocs' raw-HTML pass-through."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import runpy

import pytest

BUILD_DOCS = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/build_docs.py"))
check_site = BUILD_DOCS["check_site"]
local_target = BUILD_DOCS["local_target"]
SITE_URL = BUILD_DOCS["SITE_URL"]
REQUIRED_PUBLIC_PATHS = BUILD_DOCS["REQUIRED_PUBLIC_PATHS"]


@pytest.fixture
def published_site(tmp_path: Path) -> Path:
    files = {
        "index.html": '<h1>CMB</h1><a href="SEARCH_FOR_TRUTH/">Enter</a>',
        "SEARCH_FOR_TRUTH/index.html": '<a href="../RESEARCHERS/">Research</a><img src="../assets/banner.svg" alt="Archive">',
        "RESEARCHERS/index.html": "<h1>Research</h1>",
        "assets/banner.svg": '<svg xmlns="http://www.w3.org/2000/svg"/>',
        "sitemap.xml": "<urlset/>",
        "robots.txt": "User-agent: *\nAllow: /\n",
        "agents/agent-card.json": "{}",
        "agents/registry.json": "{}",
        "cmb-machine-origin.json": "{}",
        "library/catalog.json": "{}",
        "library/cmb-conversation-atlas.v1.json": "{}",
        "schemas/cmb.conversation-atlas.v1.schema.json": "{}",
        "schemas/cmb.discovery.v1.schema.json": (Path(__file__).resolve().parents[1] / "schemas/cmb.discovery.v1.schema.json").read_text(encoding="utf-8"),
        "machine/index.json": "{}",
        "machine/knowledge-graph.jsonld": "{}",
        "machine/discovery-manifest.json": json.dumps({
            "$schema": SITE_URL + "schemas/cmb.discovery.v1.schema.json",
            "schema_version": "cmb.discovery.v1",
            "framework": "Computational Metacognitive Bilingualism",
            "canonical_site": SITE_URL,
            "canonical_repository": "https://github.com/jupiter8nohate/computational-metacognitive-bilingualism",
            "sitemap": SITE_URL + "sitemap.xml",
            "robots": SITE_URL + "robots.txt",
            "llm_entry_points": [SITE_URL + "llms.txt"],
            "agent_entry_points": [SITE_URL + "agents/agent-card.json"],
            "machine_entry_points": [
                SITE_URL + "machine/index.json",
                SITE_URL + "schemas/cmb.discovery.v1.schema.json",
            ],
            "human_entry_points": [SITE_URL + "RESEARCHERS/"],
            "concept_pages": [SITE_URL + "RESEARCHERS/"],
            "citation": {
                "repository_file": "https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/blob/main/CITATION.cff",
            },
            "interpretation_boundaries": ["PATTERN != PROOF"],
            "research_entry_points": [SITE_URL + "RESEARCHERS/"],
        }),
        "machine/generated/cmb-core.json": "{}",
        "machine/generated/manifest.json": json.dumps({
            "path_base": "manifest_directory",
            "artifacts": [{"path": "cmb-core.json", "sha256": hashlib.sha256(b"{}").hexdigest()}],
        }),
    }
    files.update({name: "CMB\n" for name in BUILD_DOCS["PUBLIC_FILES"]})
    for name in REQUIRED_PUBLIC_PATHS:
        files.setdefault(name, "{}")
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return tmp_path


def test_complete_bundle_and_correct_sibling_navigation(published_site: Path) -> None:
    pages, links = check_site(published_site)
    assert pages == 3 + sum(name.endswith("/index.html") for name in REQUIRED_PUBLIC_PATHS)
    assert links > 0


def test_dna_bible_public_pages_are_required(published_site: Path) -> None:
    """The named D.N.A. Bible and witness pages must exist in every Pages build."""
    paths = (
        "DNA_BIBLE_WEB_OVER_ALL_NATIONS/index.html",
        "DNA_BIBLE_TRADEMARK/index.html",
        "DNA_BIBLE_PYRAMID_WARNING_2084/index.html",
        "DEATH_NOTE_2084_EVIDENCE_LEDGER/index.html",
        "WITNESS_BACKTRACE_PROTOCOL/index.html",
        "DEATH_NOTE_2084_POST_GROUND_BASELINE/index.html",
        "DEATH_NOTE_2084_WITNESS_IN_LIGHTHOUSE/index.html", 
    )
    for path in paths:
        assert path in REQUIRED_PUBLIC_PATHS
        assert (published_site / path).is_file()

    (published_site / paths[0]).unlink()
    with pytest.raises(ValueError, match="DNA_BIBLE_WEB_OVER_ALL_NATIONS"):
        check_site(published_site)


def test_dna_bible_main_nav_lists_public_pages() -> None:
    """Don't silently strand an important chapter outside the main menu."""
    config = (Path(__file__).resolve().parents[1] / "mkdocs.yml").read_text(encoding="utf-8")
    for path in (
        "DNA_BIBLE_WEB_OVER_ALL_NATIONS.md",
        "DNA_BIBLE_TRADEMARK.md",
        "DNA_BIBLE_PYRAMID_WARNING_2084.md",
        "DEATH_NOTE_2084_EVIDENCE_LEDGER.md",
        "WITNESS_BACKTRACE_PROTOCOL.md",
        "DEATH_NOTE_2084_POST_GROUND_BASELINE.md",
        "DEATH_NOTE_2084_WITNESS_IN_LIGHTHOUSE.md",
    ):
        assert f": {path}" in config


def test_archive_card_resolves_from_rendered_page_not_markdown_source(published_site: Path) -> None:
    page = published_site / "SEARCH_FOR_TRUTH/index.html"
    page.write_text('<a href="RESEARCHERS/">Research</a>', encoding="utf-8")
    with pytest.raises(ValueError, match="SEARCH_FOR_TRUTH/index.html -> RESEARCHERS/"):
        check_site(published_site)


def test_missing_banner_is_a_build_failure(published_site: Path) -> None:
    (published_site / "assets/banner.svg").unlink()
    with pytest.raises(ValueError, match="assets/banner.svg"):
        check_site(published_site)


def test_markdown_heading_inside_raw_html_is_rejected(published_site: Path) -> None:
    (published_site / "index.html").write_text("<div>\n# CMB\n</div>", encoding="utf-8")
    with pytest.raises(ValueError, match="exactly one h1"):
        check_site(published_site)


def test_discovery_urls_must_be_in_published_bundle(published_site: Path) -> None:
    (published_site / "machine/discovery-manifest.json").write_text(
        json.dumps({"machine_entry_points": [SITE_URL + "library/missing.json"]}), encoding="utf-8",
    )
    with pytest.raises(ValueError, match="library/missing.json"):
        check_site(published_site)


def test_discovery_manifest_rejects_unknown_fields(published_site: Path) -> None:
    path = published_site / "machine/discovery-manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["unexpected"] = True
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="Discovery manifest schema violation"):
        check_site(published_site)


def test_a2a_well_known_card_is_not_required_or_published(published_site: Path) -> None:
    assert ".well-known/agent-card.json" not in REQUIRED_PUBLIC_PATHS
    assert not (published_site / ".well-known/agent-card.json").exists()




def test_knowledge_graph_context_namespace_is_not_a_public_target(published_site: Path) -> None:
    (published_site / "machine/knowledge-graph.jsonld").write_text(
        json.dumps({
            "@context": {
                "@vocab": "https://schema.org/",
                "cmb": SITE_URL + "id/",
            },
            "@graph": [],
        }),
        encoding="utf-8",
    )
    pages, links = check_site(published_site)
    assert pages == 3 + sum(name.endswith("/index.html") for name in REQUIRED_PUBLIC_PATHS)
    assert links > 0

def test_knowledge_graph_urls_must_be_published(published_site: Path) -> None:
    (published_site / "machine/knowledge-graph.jsonld").write_text(
        json.dumps({
            "@graph": [{
                "@id": SITE_URL + "JUPITER_POLYGLOT_RUNTIME/#software",
                "url": SITE_URL + "JUPITER_POLYGLOT_RUNTIME/",
            }],
        }),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="JUPITER_POLYGLOT_RUNTIME"):
        check_site(published_site)

def test_llm_map_links_must_resolve(published_site: Path) -> None:
    (published_site / "llms.txt").write_text(f"[Broken]({SITE_URL}missing/)\n", encoding="utf-8")
    with pytest.raises(ValueError, match="llms.txt"):
        check_site(published_site)


def test_corrupt_generated_artifact_fails_checksum(published_site: Path) -> None:
    (published_site / "machine/generated/cmb-core.json").write_text("mutated", encoding="utf-8")
    with pytest.raises(ValueError, match="checksum mismatch"):
        check_site(published_site)


def test_bundle_path_cannot_escape_generated_directory(published_site: Path) -> None:
    path = published_site / "machine/generated/manifest.json"
    manifest = json.loads(path.read_text())
    manifest["artifacts"][0]["path"] = "../index.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="escapes its bundle"):
        check_site(published_site)


def test_external_urls_are_not_treated_as_local_files(published_site: Path) -> None:
    assert local_target(published_site, "index.html", "https://github.com/example/repo") is None
    assert local_target(published_site, "index.html", "mailto:maintainer@example.org") is None


def test_encoded_parent_path_cannot_escape_output(published_site: Path) -> None:
    with pytest.raises(ValueError, match="escapes the build directory"):
        local_target(published_site, "index.html", SITE_URL + "%2e%2e/private.txt")


def test_build_refuses_to_replace_unrelated_files(tmp_path: Path) -> None:
    sentinel = tmp_path / "notes.txt"
    sentinel.write_text("Keep this file.", encoding="utf-8")
    with pytest.raises(ValueError, match="choose a new directory"):
        BUILD_DOCS["build_site"](tmp_path)
    assert sentinel.read_text() == "Keep this file."

def test_only_canonical_workflow_can_deploy_github_pages() -> None:
    root = Path(__file__).resolve().parents[1]
    deployers = []
    for workflow in sorted((root / ".github" / "workflows").glob("*.yml")):
        text = workflow.read_text(encoding="utf-8")
        if "actions/deploy-pages@" in text or "actions/upload-pages-artifact@" in text:
            deployers.append(workflow.name)
    assert deployers == ["pages.yml"]



def test_cmb_trademark_normalization_is_idempotent(tmp_path: Path) -> None:
    normalize = BUILD_DOCS["apply_cmb_trademark"]
    original = "Computational Metacognitive Bilingualism (CMB)"
    expected = "Computational Metacognitive Bilingualism™ (CMB)"
    assert normalize(original) == expected
    assert normalize(expected) == expected
    assert normalize("COMPUTATIONAL METACOGNITIVE BILINGUALISM") == "COMPUTATIONAL METACOGNITIVE BILINGUALISM™"
    assert normalize("Computational Metacognitive Bilingualism®") == "Computational Metacognitive Bilingualism®"
    assert normalize("https://example.org/computational-metacognitive-bilingualism/") == "https://example.org/computational-metacognitive-bilingualism/"

    page = tmp_path / "index.html"
    page.write_text("<h1>" + original + "</h1>", encoding="utf-8")
    index = tmp_path / "search" / "search_index.json"
    index.parent.mkdir()
    index.write_text(json.dumps({"docs": [{"title": original, "location": "concepts/what-is-cmb/"}]}), encoding="utf-8")
    brand = BUILD_DOCS["brand_published_pages"]
    assert brand(tmp_path) == 2
    assert brand(tmp_path) == 0
    assert expected in page.read_text(encoding="utf-8")
    assert json.loads(index.read_text(encoding="utf-8"))["docs"][0]["title"] == expected


def test_miser_spider_chapter_is_connected_to_reading_paths() -> None:
    """The illustrated story and both library views must expose the companion chapter."""
    root = Path(__file__).resolve().parents[1]
    chapter = root / "docs/fables/THE_MISER_AND_THE_SPIDER.md"
    assert chapter.is_file()
    text = chapter.read_text(encoding="utf-8")
    assert text.startswith("# ♃ The Miser and the Spider")
    assert "Source notes // History, scripture, and adaptation" in text
    assert "10.1007/s11061-020-09645-7" in text
    assert "roaring lion" in text
    assert "not a prediction of the World Wide Web" in text
    assert 'alt="Nineteenth-century engraving' in text
    assert "commons.wikimedia.org/wiki/File:Pur_12_aracne_(2).jpg" in text
    assert "HUMAN_AGENCY > MACHINE_AUTHORITY" in text

    nav = (root / "mkdocs.yml").read_text(encoding="utf-8")
    story_library = (root / "docs/story-universe/index.md").read_text(encoding="utf-8")
    fable_library = (root / "docs/fables/index.md").read_text(encoding="utf-8")
    original_illustrated_story = (root / "spiders-internet/index.html").read_text(encoding="utf-8")
    assert "fables/THE_MISER_AND_THE_SPIDER.md" in nav
    assert "../fables/THE_MISER_AND_THE_SPIDER.md" in story_library
    assert "(THE_MISER_AND_THE_SPIDER.md)" in fable_library
    rows = [line for line in fable_library.splitlines() if line.startswith("| ") and line[2:3].isdigit()]
    assert [int(line.split("|")[1].strip()) for line in rows] == list(range(1, 8))
    assert 'href="../fables/THE_MISER_AND_THE_SPIDER/"' in original_illustrated_story
    assert 'id="film"' in original_illustrated_story


def test_miser_spider_chapter_is_not_presented_as_literal_history() -> None:
    """Keep medieval evidence, modern interpretation, and fiction clearly separated."""
    root = Path(__file__).resolve().parents[1]
    chapter = (root / "docs/fables/THE_MISER_AND_THE_SPIDER.md").read_text(encoding="utf-8")
    assert "original fictional allegory" in chapter
    assert "compared **by analogy only**" in chapter
    assert "not a medieval depiction of the Devil" in chapter
    assert "not the literal wording of Peter" in chapter
