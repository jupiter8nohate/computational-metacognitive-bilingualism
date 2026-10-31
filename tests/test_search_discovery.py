"""Regression tests for the public Google discovery contract."""

from pathlib import Path
import runpy

import pytest

MOD = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/check_search_discovery.py")
)
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
            f"<title>{relative or 'Home'} | Jupiter Hudson</title>"
            f'<link rel="canonical" href="{url}">'
            '<meta name="description" content="Code-poetry and human agency">'
            "</head><body><h1>CMB</h1></body></html>",
            encoding="utf-8",
        )
    (tmp_path / "sitemap.xml").write_text(
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(urls)
        + "</urlset>",
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
    homepage.write_text(
        content.replace(SITE, "https://example.invalid/"), encoding="utf-8"
    )
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
        content.replace(
            '<meta name="description" content="Code-poetry and human agency">', ""
        ),
        encoding="utf-8",
    )
    assert any("description" in message for message in verify(discovery_site))


def add_landing_page(site: Path, route: str) -> Path:
    page = site / route / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text(
        f'<html><head><title>Additional research page</title><link rel="canonical" href="{SITE}{route}">'
        '<meta name="description" content="A specific description of this research page."></head><body>Research</body></html>',
        encoding="utf-8",
    )
    sitemap = site / "sitemap.xml"
    sitemap.write_text(
        sitemap.read_text(encoding="utf-8").replace(
            "</urlset>", f"<url><loc>{SITE}{route}</loc></url></urlset>"
        ),
        encoding="utf-8",
    )
    return page


@pytest.mark.parametrize(
    "defect",
    ["noindex", "missing_description", "wrong_canonical", "duplicate_description"],
)
def test_checks_pages_outside_the_priority_sample(
    discovery_site: Path, defect: str
) -> None:
    page = add_landing_page(discovery_site, "research/new-paper/")
    content = page.read_text(encoding="utf-8")
    edits = {
        "noindex": ("</head>", '<meta name="googlebot" content="none"></head>'),
        "missing_description": (
            '<meta name="description" content="A specific description of this research page.">',
            "",
        ),
        "wrong_canonical": (SITE + "research/new-paper/", SITE + "FAQ/"),
        "duplicate_description": (
            "</head>",
            '<meta name="description" content="Conflicting description"></head>',
        ),
    }
    page.write_text(content.replace(*edits[defect]), encoding="utf-8")
    assert any("research/new-paper/" in message for message in verify(discovery_site))


def test_detects_standalone_html_missing_from_sitemap(discovery_site: Path) -> None:
    page = discovery_site / "new-story/index.html"
    page.parent.mkdir()
    page.write_text(
        "<html><head><title>New story</title></head></html>", encoding="utf-8"
    )
    assert any(
        "not listed in sitemap" in message and "new-story/" in message
        for message in verify(discovery_site)
    )


def test_duplicate_titles_and_stale_compressed_sitemap(discovery_site: Path) -> None:
    import gzip

    page = add_landing_page(discovery_site, "research/new-paper/")
    page.write_text(
        page.read_text(encoding="utf-8").replace(
            "Additional research page", "Home | Jupiter Hudson"
        ),
        encoding="utf-8",
    )
    (discovery_site / "sitemap.xml.gz").write_bytes(gzip.compress(b"outdated sitemap"))
    failures = verify(discovery_site)
    assert any("Duplicate search title" in message for message in failures)
    assert any("Compressed sitemap differs" in message for message in failures)


@pytest.mark.parametrize(
    "case", ["valid", "header_noindex", "robots_block", "robots_404"]
)
def test_live_checks_http_headers_and_host_root_policy(
    monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    def fetch(url: str) -> tuple[str, dict[str, str], int]:
        if url.endswith("/robots.txt"):
            if case == "robots_404":
                return "", {}, 404
            return (
                "User-agent: *\nDisallow: "
                + ("/" if case == "robots_block" else "")
                + "\n",
                {},
                200,
            )
        if url.endswith("/sitemap.xml"):
            return (
                (
                    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    + "".join(
                        f"<url><loc>{SITE}{route}</loc></url>" for route in KEY_PAGES
                    )
                    + "</urlset>"
                ),
                {},
                200,
            )
        return (
            (
                f'<html><head><title>A page</title><meta name="description" content="A specific description.">'
                f'<link rel="canonical" href="{url}"></head></html>'
            ),
            ({"x-robots-tag": "noindex"} if case == "header_noindex" else {}),
            200,
        )

    monkeypatch.setitem(
        MOD["verify_live_publication"].__globals__, "fetch_public_url", fetch
    )
    report = MOD["verify_live_publication"]()
    assert report["google_index_status"] == "UNKNOWN"
    assert report["publication_status"] == (
        "FAIL" if case in {"header_noindex", "robots_block"} else "PASS"
    )
