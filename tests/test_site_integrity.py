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


@pytest.fixture
def published_site(tmp_path: Path) -> Path:
    files = {
        "index.html": '<h1>CMB</h1><a href="SEARCH_FOR_TRUTH/">Enter</a>',
        "SEARCH_FOR_TRUTH/index.html": '<a href="../RESEARCHERS/">Research</a><img src="../assets/banner.svg" alt="Archive">',
        "RESEARCHERS/index.html": "<h1>Research</h1>",
        "assets/banner.svg": '<svg xmlns="http://www.w3.org/2000/svg"/>',
        "sitemap.xml": "<urlset/>",
        "robots.txt": "User-agent: *\nAllow: /\n",
        ".well-known/agent-card.json": "{}",
        "agents/agent-card.json": "{}",
        "agents/registry.json": "{}",
        "cmb-machine-origin.json": "{}",
        "library/catalog.json": "{}",
        "machine/index.json": "{}",
        "machine/knowledge-graph.jsonld": "{}",
        "machine/discovery-manifest.json": json.dumps({"human_entry_points": [SITE_URL + "RESEARCHERS/"]}),
        "machine/generated/cmb-core.json": "{}",
        "machine/generated/manifest.json": json.dumps({
            "path_base": "manifest_directory",
            "artifacts": [{"path": "cmb-core.json", "sha256": hashlib.sha256(b"{}").hexdigest()}],
        }),
    }
    files.update({name: "CMB\n" for name in BUILD_DOCS["PUBLIC_FILES"]})
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return tmp_path


def test_complete_bundle_and_correct_sibling_navigation(published_site: Path) -> None:
    pages, links = check_site(published_site)
    assert pages == 3
    assert links > 0


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

