"""Regression tests for the public Google discovery contract."""

from pathlib import Path
import runpy

import pytest

MOD = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/check_search_discovery.py"))
verify = MOD["verify_search_discovery"]
SITE = MOD["SITE_URL"]
KEY_PAGES = MOD["KEY_PAGES"]
VERIFICATION = MOD["VERIFICATION"]


@pytest.fixture
def discovery_site(tmp_path: Path) -> Path:
    urls = []
    for relative in KEY_PAGES:
        url = SITE + relative
        urls.append(f"<url><loc>{url}</loc></url>")
        target = tmp_path / relative / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "<html><head>"
            "<title>Computational Metacognitive Bilingualism | Jupiter Hudson</title>"
            f'<link rel="canonical" href="{url}">'
            '<meta name="description" content="Code-poetry and human agency">'
            "</head><body><h1>CMB</h1></body></html>",
            encoding="utf-8",
        )
    (tmp_path / "sitemap.xml").write_text(
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(urls) + "</urlset>",
        encoding="utf-8",
    )
    (tmp_path / VERIFICATION).write_text(
        f"google-site-verification: {VERIFICATION}\n", encoding="utf-8"
    )
    return tmp_path


def test_valid_publication(discovery_site: Path) -> None:
    assert verify(discovery_site) == []


def test_missing_google_ownership_file(discovery_site: Path) -> None:
    (discovery_site / VERIFICATION).unlink()
    assert any("verification" in message for message in verify(discovery_site))


def test_noindex_homepage(discovery_site: Path) -> None:
    homepage = discovery_site / "index.html"
    content = homepage.read_text(encoding="utf-8")
    homepage.write_text(
        content.replace("</head>", '<meta name="robots" content="noindex"></head>'),
        encoding="utf-8",
    )
    assert any("noindex" in message for message in verify(discovery_site))


def test_wrong_canonical(discovery_site: Path) -> None:
    homepage = discovery_site / "index.html"
    content = homepage.read_text(encoding="utf-8")
    homepage.write_text(content.replace(SITE, "https://example.invalid/"), encoding="utf-8")
    assert any("Canonical" in message for message in verify(discovery_site))


def test_sitemap_duplicate(discovery_site: Path) -> None:
    sitemap = discovery_site / "sitemap.xml"
    original = sitemap.read_text(encoding="utf-8")
    sitemap.write_text(
        original.replace("</urlset>", f"<url><loc>{SITE}</loc></url></urlset>"),
        encoding="utf-8",
    )
    assert any("Duplicate sitemap" in message for message in verify(discovery_site))


def test_sitemap_missing_target(discovery_site: Path) -> None:
    (discovery_site / "fables" / "index.html").unlink()
    failures = verify(discovery_site)
    assert any("missing published HTML" in message for message in failures)


def test_homepage_missing_description(discovery_site: Path) -> None:
    homepage = discovery_site / "index.html"
    content = homepage.read_text(encoding="utf-8")
    homepage.write_text(
        content.replace('<meta name="description" content="Code-poetry and human agency">', ""),
        encoding="utf-8",
    )
    assert any("description" in message for message in verify(discovery_site))
